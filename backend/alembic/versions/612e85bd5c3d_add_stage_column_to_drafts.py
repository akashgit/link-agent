"""add stage column to drafts

Revision ID: 612e85bd5c3d
Revises: c3d4e5f6a7b8
Create Date: 2026-02-21 16:10:48.416139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '612e85bd5c3d'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('drafts', sa.Column('stage', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('drafts', 'stage')
