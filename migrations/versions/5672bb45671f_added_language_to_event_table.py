"""added language to event table

Revision ID: 5672bb45671f
Revises: 29b874677890
Create Date: 2020-03-20 15:22:26.388864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5672bb45671f'
down_revision = '29b874677890'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'language')
    # ### end Alembic commands ###
