import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.post import ContentPillar, PostFormat

import enum


class CalendarStatus(str, enum.Enum):
    PLANNED = "planned"
    DRAFT_READY = "draft_ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


class CalendarEntry(Base):
    __tablename__ = "content_calendar"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    content_pillar: Mapped[str] = mapped_column(
        Enum(ContentPillar, name="content_pillar", create_type=False), nullable=False
    )
    post_format: Mapped[str] = mapped_column(
        Enum(PostFormat, name="post_format", create_type=False), nullable=False
    )
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(CalendarStatus, name="calendar_status"), default=CalendarStatus.PLANNED, nullable=False
    )
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
