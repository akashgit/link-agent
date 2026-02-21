from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MediaAssetResponse(BaseModel):
    id: UUID
    post_id: UUID | None
    filename: str
    file_path: str
    content_type: str
    file_size: int
    source: str | None = None
    prompt_used: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FileUploadResponse(BaseModel):
    asset: MediaAssetResponse
    extracted_text: str | None = None
    extracted_images: list[MediaAssetResponse] = []
