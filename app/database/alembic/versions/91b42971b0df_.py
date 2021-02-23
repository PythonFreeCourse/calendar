"""empty message

Revision ID: 91b42971b0df
Revises:
Create Date: 2021-02-06 16:15:07.861957

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '91b42971b0df'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_categories_id', table_name='categories')
    op.drop_table('categories')
    op.drop_index('ix_invitations_id', table_name='invitations')
    op.drop_table('invitations')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_quotes_id', table_name='quotes')
    op.drop_table('quotes')
    op.drop_index('ix_wikipedia_events_id', table_name='wikipedia_events')
    op.drop_table('wikipedia_events')
    op.drop_index('ix_zodiac-signs_id', table_name='zodiac-signs')
    op.drop_table('zodiac-signs')
    op.drop_index('ix_events_id', table_name='events')
    op.drop_table('events')
    op.drop_index('ix_user_event_id', table_name='user_event')
    op.drop_table('user_event')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_event',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('user_id', sa.INTEGER(), nullable=True),
                    sa.Column('event_id', sa.INTEGER(), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_user_event_id', 'user_event', ['id'], unique=False)
    op.create_table('events',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('title', sa.VARCHAR(), nullable=False),
                    sa.Column('start', sa.DATETIME(), nullable=False),
                    sa.Column('end', sa.DATETIME(), nullable=False),
                    sa.Column('content', sa.VARCHAR(), nullable=True),
                    sa.Column('location', sa.VARCHAR(), nullable=True),
                    sa.Column('color', sa.VARCHAR(), nullable=True),
                    sa.Column('owner_id', sa.INTEGER(), nullable=True),
                    sa.Column('category_id', sa.INTEGER(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['category_id'], ['categories.id'], ),
                    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_events_id', 'events', ['id'], unique=False)
    op.create_table('zodiac-signs',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('name', sa.VARCHAR(), nullable=False),
                    sa.Column('start_month', sa.INTEGER(), nullable=False),
                    sa.Column('start_day_in_month',
                              sa.INTEGER(), nullable=False),
                    sa.Column('end_month', sa.INTEGER(), nullable=False),
                    sa.Column('end_day_in_month',
                              sa.INTEGER(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_zodiac-signs_id', 'zodiac-signs', ['id'], unique=False)
    op.create_table('wikipedia_events',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('date_', sa.VARCHAR(), nullable=False),
                    sa.Column('wikipedia', sa.VARCHAR(), nullable=False),
                    sa.Column('events', sqlite.JSON(), nullable=True),
                    sa.Column('date_inserted', sa.DATETIME(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_wikipedia_events_id',
                    'wikipedia_events', ['id'], unique=False)
    op.create_table('quotes',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('text', sa.VARCHAR(), nullable=False),
                    sa.Column('author', sa.VARCHAR(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_quotes_id', 'quotes', ['id'], unique=False)
    op.create_table('users',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('username', sa.VARCHAR(), nullable=False),
                    sa.Column('email', sa.VARCHAR(), nullable=False),
                    sa.Column('password', sa.VARCHAR(), nullable=False),
                    sa.Column('full_name', sa.VARCHAR(), nullable=True),
                    sa.Column('language', sa.VARCHAR(), nullable=True),
                    sa.Column('description', sa.VARCHAR(), nullable=True),
                    sa.Column('avatar', sa.VARCHAR(), nullable=True),
                    sa.Column('telegram_id', sa.VARCHAR(), nullable=True),
                    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
                    sa.CheckConstraint('is_active IN (0, 1)'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('telegram_id'),
                    sa.UniqueConstraint('username')
                    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_table('invitations',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('status', sa.VARCHAR(), nullable=False),
                    sa.Column('recipient_id', sa.INTEGER(), nullable=True),
                    sa.Column('event_id', sa.INTEGER(), nullable=True),
                    sa.Column('creation', sa.DATETIME(), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
                    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_invitations_id', 'invitations', ['id'], unique=False)
    op.create_table('categories',
                    sa.Column('id', sa.INTEGER(), nullable=False),
                    sa.Column('name', sa.VARCHAR(), nullable=False),
                    sa.Column('color', sa.VARCHAR(), nullable=False),
                    sa.Column('user_id', sa.INTEGER(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id', 'name', 'color')
                    )
    op.create_index('ix_categories_id', 'categories', ['id'], unique=False)
    # ### end Alembic commands ###
