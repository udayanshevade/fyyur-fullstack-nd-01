"""empty message

Revision ID: 27dcab979049
Revises: d5438a4cf2ea
Create Date: 2021-07-05 00:41:27.495217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27dcab979049'
down_revision = 'd5438a4cf2ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    # ### end Alembic commands ###