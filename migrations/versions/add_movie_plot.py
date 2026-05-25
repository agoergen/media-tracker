"""Add plot field to Movie model

Revision ID: add_movie_plot
Revises: clean_initial
Create Date: 2026-05-25 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_movie_plot'
down_revision = 'clean_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movie', sa.Column('plot', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('movie', 'plot')
