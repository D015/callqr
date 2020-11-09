"""empty message

Revision ID: f5a1849aa46c
Revises: 13677a0c9b2d
Create Date: 2020-11-09 16:44:47.263473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a1849aa46c'
down_revision = '13677a0c9b2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('client_place', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('corporation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('group_client_places', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_user_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_client_places', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    with op.batch_alter_table('corporation', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    with op.batch_alter_table('client_place', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.drop_column('creator_user_id')

    # ### end Alembic commands ###
