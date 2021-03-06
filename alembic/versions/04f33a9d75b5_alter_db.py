"""alter db

Revision ID: 04f33a9d75b5
Revises: 0dde2b383d6b
Create Date: 2016-08-14 21:53:33.472126

"""

# revision identifiers, used by Alembic.
revision = '04f33a9d75b5'
down_revision = '0dde2b383d6b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('idx_resource_type_module', 'resource_type', ['module'], unique=False)
    op.create_index('idx_resource_type_name', 'resource_type', ['name'], unique=False)
    op.create_index('idx_resource_type_resource_name', 'resource_type', ['resource_name'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_resource_type_resource_name', table_name='resource_type')
    op.drop_index('idx_resource_type_name', table_name='resource_type')
    op.drop_index('idx_resource_type_module', table_name='resource_type')
    ### end Alembic commands ###
