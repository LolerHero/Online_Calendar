"""followers

Revision ID: 76076869d355
Revises: 85f8e8edb38d
Create Date: 2020-03-17 13:09:49.945635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76076869d355'
down_revision = '85f8e8edb38d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
