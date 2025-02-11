"""Add AI parameters to User model

Revision ID: 9ebd05fb69ed
Revises: 
Create Date: 2025-02-12 00:05:14.200293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ebd05fb69ed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('max_tokens', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('temperature', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('top_p', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('top_k', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('top_k')
        batch_op.drop_column('top_p')
        batch_op.drop_column('temperature')
        batch_op.drop_column('max_tokens')

    # ### end Alembic commands ###
