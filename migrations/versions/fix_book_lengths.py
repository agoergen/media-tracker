"""Fix book field lengths

Revision ID: fix_book_lengths
Revises: expand_book_meta
Create Date: 2026-05-26 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_book_lengths'
down_revision = 'expand_book_meta'
branch_labels = None
depends_on = None


def upgrade():
    # Change author and genres to Text
    op.alter_column('book', 'author',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)
    op.alter_column('book', 'genres',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)


def downgrade():
    op.alter_column('book', 'genres',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('book', 'author',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
