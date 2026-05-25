"""Add wikipedia_url to Movie model

Revision ID: add_movie_wiki
Revises: expand_movie_meta
Create Date: 2026-05-25 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_movie_wiki'
down_revision = 'expand_movie_meta'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movie', sa.Column('wikipedia_url', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('movie', 'wikipedia_url')
