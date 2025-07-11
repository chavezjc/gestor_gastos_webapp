"""Permitir rol nulo y nuevo flujo de asignacion

Revision ID: c23aab13b8a4
Revises: 3c4597b1d8fb
Create Date: 2025-06-18 08:56:45.200443

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c23aab13b8a4'
down_revision = '3c4597b1d8fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('personal', schema=None) as batch_op:
        batch_op.alter_column('rol',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('personal', schema=None) as batch_op:
        batch_op.alter_column('rol',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50),
               nullable=False)

    # ### end Alembic commands ###
