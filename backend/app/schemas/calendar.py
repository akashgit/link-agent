from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class CalendarEntryCreate(BaseModel):
    scheduled_date: date
    content_pillar: str
    post_format: str
    topic: str
    notes: str | None = None


class CalendarEntryUpdate(BaseModel):
    scheduled_date: date | None = None
    topic: str | None = None
    status: str | None = None
    post_id: UUID | None = None
    notes: str | None = None


class CalendarEntryResponse(BaseModel):
    id: UUID
    scheduled_date: date
    content_pillar: str
    post_format: str
    topic: str
    status: str
    post_id: UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
