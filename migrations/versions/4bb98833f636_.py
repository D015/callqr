"""empty message

Revision ID: 4bb98833f636
Revises: 5ccf0d6731f9
Create Date: 2020-06-14 01:14:04.748452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bb98833f636'
down_revision = '5ccf0d6731f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client_place', schema=None) as batch_op:
        batch_op.add_column(sa.Column('group_client_places_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'group_client_places', ['group_client_places_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client_place', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('group_client_places_id')

    # ### end Alembic commands ###
