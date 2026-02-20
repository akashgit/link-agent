import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

import enum


class PostStatus(str, enum.Enum):
    IDEA = "idea"
    DRAFTING = "drafting"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


class ContentPillar(str, enum.Enum):
    AGENTOPS = "agentops"
    INFERENCE_SCALING = "inference_scaling"
    ENTERPRISE_REALITY = "enterprise_reality"
    RESEARCH_TO_PRODUCT = "research_to_product"
    LEADERSHIP = "leadership"


class PostFormat(str, enum.Enum):
    FRAMEWORK = "framework"
    STRONG_POV = "strong_pov"
    SIMPLIFICATION = "simplification"
    STORY = "story"
    LEADER_LENS = "leader_lens"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_pillar: Mapped[str] = mapped_column(
        Enum(ContentPillar, name="content_pillar"), nullable=False
    )
    post_format: Mapped[str] = mapped_column(
        Enum(PostFormat, name="post_format"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(PostStatus, name="post_status"), default=PostStatus.IDEA, nullable=False
    )
    final_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    drafts: Mapped[list["Draft"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class Draft(Base):
    __tablename__ = "drafts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    post: Mapped["Post"] = relationship(back_populates="drafts")
