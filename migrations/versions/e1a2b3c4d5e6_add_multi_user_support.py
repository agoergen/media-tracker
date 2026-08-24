"""Add multi user support with closed registration and user_id relations

Revision ID: e1a2b3c4d5e6
Revises: d6910e02b08d
Create Date: 2026-08-24 13:28:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1a2b3c4d5e6'
down_revision = '7ba2ae3915b3'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Update user table to include is_admin
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))

    # Promote existing user(s) to admin
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE \"user\" SET is_admin = true" if conn.dialect.name == 'postgresql' else "UPDATE user SET is_admin = 1"))

    # 2. Create invite_token table for closed onboarding
    op.create_table(
        'invite_token',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('used_by_user_id', sa.Integer(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['used_by_user_id'], ['user.id'], name='fk_invite_token_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('invite_token', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_invite_token_token'), ['token'], unique=True)

    # 3. Add user_id foreign keys and indexes to all user-owned media models
    models_to_update = [
        ('movie', 'fk_movie_user_id', 'ix_movie_user_id'),
        ('game', 'fk_game_user_id', 'ix_game_user_id'),
        ('book', 'fk_book_user_id', 'ix_book_user_id'),
        ('theater', 'fk_theater_user_id', 'ix_theater_user_id'),
        ('tv_season', 'fk_tv_season_user_id', 'ix_tv_season_user_id'),
        ('future_media_goal', 'fk_future_media_goal_user_id', 'ix_future_media_goal_user_id'),
        ('backlog_item', 'fk_backlog_item_user_id', 'ix_backlog_item_user_id')
    ]

    for table_name, fk_name, idx_name in models_to_update:
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            batch_op.add_column(sa.Column('user_id', sa.Integer(), server_default='1', nullable=False))
            batch_op.create_index(batch_op.f(idx_name), ['user_id'], unique=False)
            batch_op.create_foreign_key(fk_name, 'user', ['user_id'], ['id'])

    # 4. Update goal table constraints and add user_id
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), server_default='1', nullable=False))
        batch_op.create_index(batch_op.f('ix_goal_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_goal_user_id', 'user', ['user_id'], ['id'])
        try:
            batch_op.drop_constraint('unique_year_goal', type_='unique')
        except Exception:
            pass
        batch_op.create_unique_constraint('unique_user_year_goal', ['user_id', 'year'])


def downgrade():
    # Revert goal table
    with op.batch_alter_table('goal', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('unique_user_year_goal', type_='unique')
        except Exception:
            pass
        batch_op.create_unique_constraint('unique_year_goal', ['year'])
        batch_op.drop_constraint('fk_goal_user_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_goal_user_id'))
        batch_op.drop_column('user_id')

    # Revert media tables
    models_to_revert = [
        ('backlog_item', 'fk_backlog_item_user_id', 'ix_backlog_item_user_id'),
        ('future_media_goal', 'fk_future_media_goal_user_id', 'ix_future_media_goal_user_id'),
        ('tv_season', 'fk_tv_season_user_id', 'ix_tv_season_user_id'),
        ('theater', 'fk_theater_user_id', 'ix_theater_user_id'),
        ('book', 'fk_book_user_id', 'ix_book_user_id'),
        ('game', 'fk_game_user_id', 'ix_game_user_id'),
        ('movie', 'fk_movie_user_id', 'ix_movie_user_id')
    ]

    for table_name, fk_name, idx_name in models_to_revert:
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')
            batch_op.drop_index(batch_op.f(idx_name))
            batch_op.drop_column('user_id')

    # Drop invite_token table
    with op.batch_alter_table('invite_token', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_invite_token_token'))
    op.drop_table('invite_token')

    # Revert user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')
