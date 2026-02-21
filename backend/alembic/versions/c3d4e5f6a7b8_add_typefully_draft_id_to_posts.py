"""add typefully_draft_id to posts

Revision ID: c3d4e5f6a7b8
Revises: b2f3a4c5d6e7
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2f3a4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("typefully_draft_id", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("posts", "typefully_draft_id")
