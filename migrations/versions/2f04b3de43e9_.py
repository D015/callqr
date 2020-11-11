"""empty message

Revision ID: 2f04b3de43e9
Revises: f5a1849aa46c
Create Date: 2020-11-10 19:01:49.881135

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2f04b3de43e9'
down_revision = 'f5a1849aa46c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('base_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('creator_user_id', sa.Integer(), nullable=True),
    sa.Column('slug', sa.String(length=128), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.Column('about', sa.String(length=140), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('corporation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['corporation_id'], ['corporation.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('base_model', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_base_model_slug'), ['slug'], unique=True)

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_index('ix_client_slug')

    op.drop_table('client')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('about', sa.VARCHAR(length=140), autoincrement=False, nullable=True),
    sa.Column('slug', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('corporation_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('archived', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('creator_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['corporation_id'], ['corporation.id'], name='client_corporation_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='client_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='client_pkey')
    )
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.create_index('ix_client_slug', ['slug'], unique=True)

    with op.batch_alter_table('base_model', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_base_model_slug'))

    op.drop_table('base_model')
    # ### end Alembic commands ###