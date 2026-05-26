"""Add Theater and TheaterReference tables

Revision ID: add_theater_tables
Revises: add_book_url
Create Date: 2026-05-26 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_theater_tables'
down_revision = 'add_book_url'
branch_labels = None
depends_on = None


def upgrade():
    # Update existing theater table if it exists, or create fresh
    # First, let's ensure we can handle existing columns
    try:
        op.drop_table('theater')
    except:
        pass
        
    op.create_table('theater',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('date_watched', sa.Date(), nullable=True),
        sa.Column('is_revisit', sa.Boolean(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('original_theater', sa.String(length=255), nullable=True),
        sa.Column('run_time', sa.Integer(), nullable=True),
        sa.Column('show_type', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('theater_reference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('show_name', sa.String(length=255), nullable=False),
        sa.Column('show_type', sa.String(length=100), nullable=True),
        sa.Column('theatre', sa.String(length=255), nullable=True),
        sa.Column('date_open', sa.String(length=50), nullable=True),
        sa.Column('date_close', sa.String(length=50), nullable=True),
        sa.Column('run_time_minutes', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('theater_reference')
    op.drop_table('theater')
