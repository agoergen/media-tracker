"""Add theater summary and remove reference table

Revision ID: theater_pure_ibdb
Revises: add_theater_poster
Create Date: 2026-05-26 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'theater_pure_ibdb'
down_revision = 'add_theater_poster'
branch_labels = None
depends_on = None


def upgrade():
    # Add summary column to theater
    op.add_column('theater', sa.Column('summary', sa.Text(), nullable=True))
    
    # Drop theater_reference table
    op.drop_table('theater_reference')


def downgrade():
    # Recreate theater_reference table
    op.create_table('theater_reference',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('show_name', sa.Text(), nullable=False),
        sa.Column('show_type', sa.String(length=100), nullable=True),
        sa.Column('theatre', sa.Text(), nullable=True),
        sa.Column('date_open', sa.String(length=50), nullable=True),
        sa.Column('date_close', sa.String(length=50), nullable=True),
        sa.Column('run_time_minutes', sa.Integer(), nullable=True)
    )
    
    # Remove summary column
    op.drop_column('theater', 'summary')
