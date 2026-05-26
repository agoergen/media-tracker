"""Fix theater field lengths

Revision ID: fix_theater_lengths
Revises: add_theater_tables
Create Date: 2026-05-26 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_theater_lengths'
down_revision = 'add_theater_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Change show_name and theatre to Text for both tables
    op.alter_column('theater', 'title',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=False)
    op.alter_column('theater', 'original_theater',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)
    
    op.alter_column('theater_reference', 'show_name',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=False)
    op.alter_column('theater_reference', 'theatre',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)


def downgrade():
    op.alter_column('theater_reference', 'theatre',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('theater_reference', 'show_name',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    op.alter_column('theater', 'original_theater',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    op.alter_column('theater', 'title',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
