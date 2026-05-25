"""Increase director and writer field length

Revision ID: fix_truncation
Revises: add_movie_writer
Create Date: 2026-05-25 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_truncation'
down_revision = 'add_movie_writer'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('movie', 'director', type_=sa.Text())
    op.alter_column('movie', 'writer', type_=sa.Text())


def downgrade():
    op.alter_column('movie', 'director', type_=sa.String(255))
    op.alter_column('movie', 'writer', type_=sa.String(255))
