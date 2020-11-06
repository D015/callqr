"""empty message

Revision ID: 7cfe7b8b494e
Revises: 25397d1a9199
Create Date: 2020-11-06 23:02:09.901042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cfe7b8b494e'
down_revision = '25397d1a9199'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_admin_phone'), ['phone'], unique=True)
        batch_op.drop_constraint('admin_phone_key', type_='unique')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))

    with op.batch_alter_table('client_place', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.drop_index('ix_client_place_name')

    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.drop_index('ix_company_name')

    with op.batch_alter_table('corporation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.drop_index('ix_corporation_name')

    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_employee_phone'), ['phone'], unique=True)
        batch_op.drop_constraint('employee_phone_key', type_='unique')
        batch_op.drop_index('ix_employee_first_name')
        batch_op.drop_index('ix_employee_last_name')

    with op.batch_alter_table('group_client_places', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))
        batch_op.drop_index('ix_group_client_places_name')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('archived')

    with op.batch_alter_table('group_client_places', schema=None) as batch_op:
        batch_op.create_index('ix_group_client_places_name', ['name'], unique=False)
        batch_op.drop_column('archived')
        batch_op.drop_column('active')

    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.create_index('ix_employee_last_name', ['last_name'], unique=False)
        batch_op.create_index('ix_employee_first_name', ['first_name'], unique=False)
        batch_op.create_unique_constraint('employee_phone_key', ['phone'])
        batch_op.drop_index(batch_op.f('ix_employee_phone'))
        batch_op.drop_column('timestamp')
        batch_op.drop_column('archived')
        batch_op.drop_column('active')

    with op.batch_alter_table('corporation', schema=None) as batch_op:
        batch_op.create_index('ix_corporation_name', ['name'], unique=False)
        batch_op.drop_column('archived')
        batch_op.drop_column('active')

    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.create_index('ix_company_name', ['name'], unique=False)
        batch_op.drop_column('archived')
        batch_op.drop_column('active')

    with op.batch_alter_table('client_place', schema=None) as batch_op:
        batch_op.create_index('ix_client_place_name', ['name'], unique=False)
        batch_op.drop_column('archived')
        batch_op.drop_column('active')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('timestamp')
        batch_op.drop_column('archived')
        batch_op.drop_column('active')

    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.create_unique_constraint('admin_phone_key', ['phone'])
        batch_op.drop_index(batch_op.f('ix_admin_phone'))
        batch_op.drop_column('timestamp')
        batch_op.drop_column('archived')

    # ### end Alembic commands ###
