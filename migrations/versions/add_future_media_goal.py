"""Add future media goal model

Revision ID: add_future_media_goal
Revises: force_fix_goal
Create Date: 2026-05-27 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_future_media_goal'
down_revision = 'force_fix_goal'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('future_media_goal',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=True)
    )


def downgrade():
    op.drop_table('future_media_goal')
