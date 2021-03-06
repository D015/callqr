"""empty message

Revision ID: 612e6e5540cf
Revises: c2ddf7cd6f89
Create Date: 2020-11-13 22:13:57.153702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '612e6e5540cf'
down_revision = 'c2ddf7cd6f89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.drop_index('ix_admin_email')
        batch_op.create_index(batch_op.f('ix_admin_email'), ['email'], unique=False)
        batch_op.drop_index('ix_admin_phone')
        batch_op.create_index(batch_op.f('ix_admin_phone'), ['phone'], unique=False)

    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_index('ix_employee_email')
        batch_op.create_index(batch_op.f('ix_employee_email'), ['email'], unique=False)
        batch_op.drop_index('ix_employee_phone')
        batch_op.create_index(batch_op.f('ix_employee_phone'), ['phone'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_employee_phone'))
        batch_op.create_index('ix_employee_phone', ['phone'], unique=True)
        batch_op.drop_index(batch_op.f('ix_employee_email'))
        batch_op.create_index('ix_employee_email', ['email'], unique=True)

    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_admin_phone'))
        batch_op.create_index('ix_admin_phone', ['phone'], unique=True)
        batch_op.drop_index(batch_op.f('ix_admin_email'))
        batch_op.create_index('ix_admin_email', ['email'], unique=True)

    # ### end Alembic commands ###
