"""Add Google Books URL to Book

Revision ID: add_book_url
Revises: fix_book_lengths
Create Date: 2026-05-26 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_book_url'
down_revision = 'fix_book_lengths'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('book', sa.Column('google_books_url', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('book', 'google_books_url')
