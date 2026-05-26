"""Expand Game metadata

Revision ID: expand_game_meta
Revises: add_user_model
Create Date: 2026-05-25 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'expand_game_meta'
down_revision = 'add_user_model'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('game', sa.Column('developer', sa.String(length=255), nullable=True))
    op.add_column('game', sa.Column('variant', sa.String(length=100), nullable=True))
    op.add_column('game', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('game', sa.Column('genres', sa.String(length=255), nullable=True))
    op.add_column('game', sa.Column('user_score', sa.Float(), nullable=True))
    op.add_column('game', sa.Column('critic_score', sa.Float(), nullable=True))
    op.add_column('game', sa.Column('poster_path', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('game', 'poster_path')
    op.drop_column('game', 'critic_score')
    op.drop_column('game', 'user_score')
    op.drop_column('game', 'genres')
    op.drop_column('game', 'summary')
    op.drop_column('game', 'variant')
    op.drop_column('game', 'developer')
