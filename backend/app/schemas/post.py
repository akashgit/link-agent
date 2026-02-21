from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content_pillar: str
    post_format: str
    user_input: str | None = None
    uploaded_file_text: str | None = None


class PostUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    final_content: str | None = None


class DraftResponse(BaseModel):
    id: UUID
    post_id: UUID
    version: int
    content: str
    hook: str | None
    cta: str | None
    hashtags: str | None
    feedback: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: UUID
    title: str
    content_pillar: str
    post_format: str
    status: str
    final_content: str | None
    thread_id: str | None
    user_input: str | None
    uploaded_file_text: str | None
    revision_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostWithDrafts(PostResponse):
    drafts: list[DraftResponse] = []
