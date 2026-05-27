"""Add goal model

Revision ID: add_goal_model
Revises: theater_pure_ibdb
Create Date: 2026-05-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_goal_model'
down_revision = 'theater_pure_ibdb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('goal',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('movie_goal', sa.Integer(), nullable=True),
        sa.Column('tv_goal', sa.Integer(), nullable=True),
        sa.Column('game_goal', sa.Integer(), nullable=True),
        sa.Column('book_goal', sa.Integer(), nullable=True),
        sa.UniqueConstraint('year', name='unique_year_goal')
    )


def downgrade():
    op.drop_table('goal')
