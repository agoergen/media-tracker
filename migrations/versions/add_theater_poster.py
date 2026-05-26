"""Add poster_path to theater

Revision ID: add_theater_poster
Revises: fix_theater_lengths
Create Date: 2026-05-26 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_theater_poster'
down_revision = 'fix_theater_lengths'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('theater', sa.Column('poster_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('theater', 'poster_path')
