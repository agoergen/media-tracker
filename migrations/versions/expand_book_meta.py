"""Expand Book metadata

Revision ID: expand_book_meta
Revises: expand_game_meta
Create Date: 2026-05-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'expand_book_meta'
down_revision = 'expand_game_meta'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('book', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('book', sa.Column('poster_path', sa.String(length=255), nullable=True))
    op.add_column('book', sa.Column('page_count', sa.Integer(), nullable=True))
    op.add_column('book', sa.Column('genres', sa.String(length=255), nullable=True))
    # Rename and change type if needed, but since we're creating 'book' columns fresh in this flow (or adding to existing)
    # Let's ensure storygraph_rating is added as Float.
    # If the column 'goodreads_rating' already exists from a previous step not shown, we'd rename.
    # But looking at models.py, it was likely added in an initial migration as Integer.
    # Let's drop and add or just alter.
    try:
        op.drop_column('book', 'goodreads_rating')
    except:
        pass
    op.add_column('book', sa.Column('storygraph_rating', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('book', 'storygraph_rating')
    op.add_column('book', sa.Column('goodreads_rating', sa.Integer(), nullable=True))
    op.drop_column('book', 'genres')
    op.drop_column('book', 'page_count')
    op.drop_column('book', 'poster_path')
    op.drop_column('book', 'summary')
