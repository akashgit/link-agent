"""add uploaded_file_text to posts and source to media_assets

Revision ID: b2f3a4c5d6e7
Revises: 0a001e882835
Create Date: 2026-02-21 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f3a4c5d6e7'
down_revision: Union[str, None] = '0a001e882835'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('uploaded_file_text', sa.Text(), nullable=True))
    op.add_column('media_assets', sa.Column('source', sa.String(length=20), server_default='uploaded', nullable=False))


def downgrade() -> None:
    op.drop_column('media_assets', 'source')
    op.drop_column('posts', 'uploaded_file_text')
