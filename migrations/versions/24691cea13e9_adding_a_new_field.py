"""adding a new field

Revision ID: 24691cea13e9
Revises: 95fe9971f4a1
Create Date: 2020-09-23 12:19:03.072963

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '24691cea13e9'
down_revision = '95fe9971f4a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sharings', sa.Column('root_folder', sa.String(length=2048), nullable=True))
    op.alter_column('sharings', 'issue',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sharings', 'issue',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_column('sharings', 'root_folder')
    # ### end Alembic commands ###
