"""Expand TVSeason metadata

Revision ID: expand_tv_meta
Revises: fix_truncation
Create Date: 2026-05-25 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'expand_tv_meta'
down_revision = 'fix_truncation'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tv_season', sa.Column('poster_path', sa.String(length=255), nullable=True))
    op.add_column('tv_season', sa.Column('user_score', sa.Float(), nullable=True))
    op.add_column('tv_season', sa.Column('plot', sa.Text(), nullable=True))
    op.add_column('tv_season', sa.Column('trailer_url', sa.String(length=255), nullable=True))
    op.add_column('tv_season', sa.Column('imdb_id', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('tv_season', 'imdb_id')
    op.drop_column('tv_season', 'trailer_url')
    op.drop_column('tv_season', 'plot')
    op.drop_column('tv_season', 'user_score')
    op.drop_column('tv_season', 'poster_path')
