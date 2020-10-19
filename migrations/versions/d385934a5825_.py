"""empty message

Revision ID: d385934a5825
Revises: 791c63b4f312
Create Date: 2020-10-19 15:00:16.156796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd385934a5825'
down_revision = '791c63b4f312'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_client_places', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about', sa.String(length=140), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_client_places', schema=None) as batch_op:
        batch_op.drop_column('about')

    # ### end Alembic commands ###
