from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.post import Post
from app.services import typefully as typefully_service
from app.utils.linkedin import validate_linkedin_post
from app.config import settings

router = APIRouter(prefix="/typefully", tags=["typefully"])


class ValidateRequest(BaseModel):
    content: str


class DraftRequest(BaseModel):
    post_id: UUID


class ScheduleRequest(BaseModel):
    post_id: UUID
    publish_at: str


@router.get("/profile")
async def get_typefully_profile():
    """Get LinkedIn profile info from the connected Typefully social set."""
    if not settings.typefully_api_key:
        raise HTTPException(status_code=400, detail="Typefully API key not configured")
    if not settings.typefully_social_set_id:
        raise HTTPException(status_code=400, detail="Typefully social set ID not configured")
    try:
        return await typefully_service.get_linkedin_profile()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch profile: {e}")


@router.post("/validate")
async def validate_content(body: ValidateRequest):
    """Validate content against LinkedIn formatting constraints."""
    return validate_linkedin_post(body.content)


@router.post("/draft")
async def create_typefully_draft(
    body: DraftRequest,
    db: AsyncSession = Depends(get_db),
):
    """Push a post's final content to Typefully as a draft."""
    if not settings.typefully_api_key:
        raise HTTPException(status_code=400, detail="Typefully API key not configured")

    result = await db.execute(select(Post).where(Post.id == body.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.final_content:
        raise HTTPException(status_code=400, detail="Post has no final content")

    # Get hashtags from the latest draft
    hashtags: list[str] = []
    if post.drafts:
        latest_draft = sorted(post.drafts, key=lambda d: d.version, reverse=True)[0]
        if latest_draft.hashtags:
            hashtags = [h.strip() for h in latest_draft.hashtags.split(",") if h.strip()]

    draft = await typefully_service.create_draft(
        text=post.final_content,
        hashtags=hashtags or None,
    )

    draft_id = draft.get("id", "")
    post.typefully_draft_id = str(draft_id)
    await db.commit()

    return {"draft_id": draft_id}


@router.post("/schedule")
async def schedule_typefully_draft(
    body: ScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    """Schedule (or create + schedule) a Typefully draft."""
    if not settings.typefully_api_key:
        raise HTTPException(status_code=400, detail="Typefully API key not configured")

    result = await db.execute(select(Post).where(Post.id == body.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.final_content:
        raise HTTPException(status_code=400, detail="Post has no final content")

    if post.typefully_draft_id:
        # Update existing draft schedule
        draft = await typefully_service.schedule_draft(
            draft_id=post.typefully_draft_id,
            publish_at=body.publish_at,
        )
    else:
        # Create new draft with schedule
        hashtags: list[str] = []
        if post.drafts:
            latest_draft = sorted(post.drafts, key=lambda d: d.version, reverse=True)[0]
            if latest_draft.hashtags:
                hashtags = [h.strip() for h in latest_draft.hashtags.split(",") if h.strip()]

        draft = await typefully_service.create_draft(
            text=post.final_content,
            hashtags=hashtags or None,
            publish_at=body.publish_at,
        )
        draft_id = draft.get("id", "")
        post.typefully_draft_id = str(draft_id)
        await db.commit()

    return {"draft_id": post.typefully_draft_id}


@router.get("/draft/{post_id}")
async def get_typefully_draft_status(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the Typefully draft status for a post."""
    if not settings.typefully_api_key:
        raise HTTPException(status_code=400, detail="Typefully API key not configured")

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.typefully_draft_id:
        raise HTTPException(status_code=404, detail="No Typefully draft for this post")

    draft = await typefully_service.get_draft(post.typefully_draft_id)
    return {"status": draft.get("status", "unknown"), "draft": draft}
