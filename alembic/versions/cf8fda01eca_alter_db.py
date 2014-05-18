"""alter db

Revision ID: cf8fda01eca
Revises: 18106941cc0d
Create Date: 2014-05-17 16:22:54.914278

"""

# revision identifiers, used by Alembic.
revision = 'cf8fda01eca'
down_revision = '18106941cc0d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service', 'currency_id')
    op.drop_column('service', 'price')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('price', sa.NUMERIC(precision=16, scale=2), nullable=False))
    op.add_column('service', sa.Column('currency_id', sa.INTEGER(), nullable=False))
    ### end Alembic commands ###
