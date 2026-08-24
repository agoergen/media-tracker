"""Add is_up_next_public to user

Revision ID: b4d5e6f7a8b9
Revises: f2b3c4d5e6a7
Create Date: 2026-08-24 14:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4d5e6f7a8b9'
down_revision = 'f2b3c4d5e6a7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_up_next_public', sa.Boolean(), server_default='false', nullable=False))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_up_next_public')
