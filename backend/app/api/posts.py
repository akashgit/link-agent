import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import get_db
from app.models.post import Post, Draft
from app.models.media_asset import MediaAsset, MediaSource
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostWithDrafts, DraftResponse
from app.schemas.media import MediaAssetResponse

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostResponse])
async def list_posts(
    status: str | None = None,
    content_pillar: str | None = None,
    post_format: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Post).order_by(Post.created_at.desc())
    if status:
        query = query.where(Post.status == status)
    if content_pillar:
        query = query.where(Post.content_pillar == content_pillar)
    if post_format:
        query = query.where(Post.post_format == post_format)
    if search:
        query = query.where(Post.title.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_db)):
    post = Post(**data.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostWithDrafts)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post).where(Post.id == post_id).options(selectinload(Post.drafts))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: UUID, data: PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.commit()


@router.get("/{post_id}/versions", response_model=list[DraftResponse])
async def get_post_versions(post_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Draft).where(Draft.post_id == post_id).order_by(Draft.version.desc())
    )
    return result.scalars().all()


@router.get("/{post_id}/media", response_model=list[MediaAssetResponse])
async def list_post_media(post_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MediaAsset)
        .where(MediaAsset.post_id == post_id)
        .order_by(MediaAsset.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{post_id}/media", response_model=MediaAssetResponse, status_code=201)
async def upload_post_media(
    post_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Verify post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    import uuid as uuid_mod

    file_id = str(uuid_mod.uuid4())
    ext = os.path.splitext(file.filename or "file")[1]
    filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.upload_dir, filename)

    os.makedirs(settings.upload_dir, exist_ok=True)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    asset = MediaAsset(
        post_id=post_id,
        filename=file.filename or filename,
        file_path=file_path,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        source=MediaSource.UPLOADED,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{post_id}/media/{asset_id}", status_code=204)
async def delete_post_media(
    post_id: UUID,
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.id == asset_id,
            MediaAsset.post_id == post_id,
        )
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Media asset not found")

    # Delete file from disk
    if os.path.exists(asset.file_path):
        os.remove(asset.file_path)

    await db.delete(asset)
    await db.commit()
