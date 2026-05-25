"""Add poster_path field to Movie model

Revision ID: add_movie_poster
Revises: add_movie_plot
Create Date: 2026-05-25 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_movie_poster'
down_revision = 'add_movie_plot'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movie', sa.Column('poster_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('movie', 'poster_path')
