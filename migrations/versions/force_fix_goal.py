"""Force fix goal table

Revision ID: force_fix_goal
Revises: add_goal_model
Create Date: 2026-05-27 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'force_fix_goal'
down_revision = 'add_goal_model'
branch_labels = None
depends_on = None


def upgrade():
    # Unconditionally drop if exists and recreate
    op.execute('DROP TABLE IF EXISTS goal CASCADE')
    
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
