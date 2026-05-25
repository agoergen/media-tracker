"""Add writer field to Movie model

Revision ID: add_movie_writer
Revises: add_movie_wiki
Create Date: 2026-05-25 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_movie_writer'
down_revision = 'add_movie_wiki'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movie', sa.Column('writer', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('movie', 'writer')
