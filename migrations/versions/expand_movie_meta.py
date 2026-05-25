"""Add expanded movie metadata fields

Revision ID: expand_movie_meta
Revises: add_movie_poster
Create Date: 2026-05-25 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'expand_movie_meta'
down_revision = 'add_movie_poster'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movie', sa.Column('imdb_id', sa.String(length=20), nullable=True))
    op.add_column('movie', sa.Column('user_score', sa.Float(), nullable=True))
    op.add_column('movie', sa.Column('runtime', sa.Integer(), nullable=True))
    op.add_column('movie', sa.Column('certification', sa.String(length=20), nullable=True))
    op.add_column('movie', sa.Column('budget', sa.BigInteger(), nullable=True))
    op.add_column('movie', sa.Column('revenue', sa.BigInteger(), nullable=True))
    op.add_column('movie', sa.Column('trailer_url', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('movie', 'trailer_url')
    op.drop_column('movie', 'revenue')
    op.drop_column('movie', 'budget')
    op.drop_column('movie', 'certification')
    op.drop_column('movie', 'runtime')
    op.drop_column('movie', 'user_score')
    op.drop_column('movie', 'imdb_id')
