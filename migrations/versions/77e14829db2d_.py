"""empty message

Revision ID: 77e14829db2d
Revises: d2c804c05e45
Create Date: 2020-06-15 00:39:38.192269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77e14829db2d'
down_revision = 'd2c804c05e45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_company_name'), ['name'], unique=False)
        batch_op.drop_index('ix_company_name_company')
        batch_op.drop_column('name_company')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name_company', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
        batch_op.create_index('ix_company_name_company', ['name_company'], unique=False)
        batch_op.drop_index(batch_op.f('ix_company_name'))
        batch_op.drop_column('name')

    # ### end Alembic commands ###