"""Add private flag to media models

Revision ID: 9cbcd953e351
Revises: add_future_media_goal
Create Date: 2026-06-06 08:42:48.905334

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cbcd953e351'
down_revision = 'add_future_media_goal'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('book', sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('game', sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('movie', sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('theater', sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('tv_season', sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False))


def downgrade():
    op.drop_column('tv_season', 'is_private')
    op.drop_column('theater', 'is_private')
    op.drop_column('movie', 'is_private')
    op.drop_column('game', 'is_private')
    op.drop_column('book', 'is_private')
