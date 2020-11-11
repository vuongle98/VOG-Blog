"""empty message

Revision ID: 88f525f89f54
Revises: dd31701f9185
Create Date: 2020-04-30 18:36:35.608624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88f525f89f54'
down_revision = 'dd31701f9185'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    # ### end Alembic commands ###