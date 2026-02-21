import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db
from app.models.media_asset import MediaAsset, MediaSource
from app.schemas.media import MediaAssetResponse, FileUploadResponse
from app.services.file_parser import parse_file

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "image/png",
    "image/jpeg",
}

DOCUMENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
}


@router.post("", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "file")[1]
    filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.upload_dir, filename)

    os.makedirs(settings.upload_dir, exist_ok=True)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    asset = MediaAsset(
        filename=file.filename or filename,
        file_path=file_path,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        source=MediaSource.UPLOADED,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    # Parse document types for text and image extraction
    extracted_text = None
    extracted_images = []

    if file.content_type in DOCUMENT_TYPES:
        parse_result = await parse_file(content, file.content_type)
        extracted_text = parse_result.text or None

        # Create MediaAsset records for each extracted image
        for img_info in parse_result.images:
            img_asset = MediaAsset(
                post_id=asset.post_id,
                filename=img_info["filename"],
                file_path=img_info["file_path"],
                content_type=img_info["content_type"],
                file_size=os.path.getsize(img_info["file_path"]),
                source=MediaSource.EXTRACTED,
            )
            db.add(img_asset)
            extracted_images.append(img_asset)

        if extracted_images:
            await db.commit()
            for img_asset in extracted_images:
                await db.refresh(img_asset)

    return FileUploadResponse(
        asset=MediaAssetResponse.model_validate(asset),
        extracted_text=extracted_text,
        extracted_images=[MediaAssetResponse.model_validate(img) for img in extracted_images],
    )


@router.get("/file/{filename}")
async def serve_file(filename: str):
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.upload_dir, safe_filename)

    # Verify the resolved path is within upload_dir
    resolved = os.path.realpath(file_path)
    upload_dir_resolved = os.path.realpath(settings.upload_dir)
    if not resolved.startswith(upload_dir_resolved):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(resolved):
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type from extension
    ext = os.path.splitext(safe_filename)[1].lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(resolved, media_type=media_type)


@router.get("/{asset_id}")
async def get_upload(asset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaAsset).where(MediaAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not os.path.exists(asset.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(asset.file_path, media_type=asset.content_type, filename=asset.filename)
