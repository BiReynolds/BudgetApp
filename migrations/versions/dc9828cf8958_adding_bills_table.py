"""Adding bills table

Revision ID: dc9828cf8958
Revises: 
Create Date: 2024-04-21 17:43:49.953268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc9828cf8958'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('amount', sa.Float(precision=8), nullable=False),
    sa.Column('nextDue', sa.Date(), nullable=False),
    sa.Column('monthInc', sa.Integer(), nullable=False),
    sa.Column('dayInc', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bill_name'), ['name'], unique=True)
        batch_op.create_index(batch_op.f('ix_bill_nextDue'), ['nextDue'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bill_nextDue'))
        batch_op.drop_index(batch_op.f('ix_bill_name'))

    op.drop_table('bill')
    # ### end Alembic commands ###
