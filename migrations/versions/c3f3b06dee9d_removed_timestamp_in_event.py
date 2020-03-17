"""Removed timestamp in Event

Revision ID: c3f3b06dee9d
Revises: 9973c67f5149
Create Date: 2020-03-17 11:35:55.882658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f3b06dee9d'
down_revision = '9973c67f5149'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_event_timestamp', table_name='event')
    op.drop_column('event', 'timestamp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('timestamp', sa.DATETIME(), nullable=True))
    op.create_index('ix_event_timestamp', 'event', ['timestamp'], unique=False)
    # ### end Alembic commands ###
