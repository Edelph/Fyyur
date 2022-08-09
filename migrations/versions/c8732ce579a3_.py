"""empty message

Revision ID: c8732ce579a3
Revises: 2cd7951e0322
Create Date: 2022-08-09 21:38:46.872047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8732ce579a3'
down_revision = '2cd7951e0322'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('Venue_id', sa.Integer(), nullable=True),
    sa.Column('Artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['Artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['Venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('Artist_id')
    )
    op.add_column('Venue', sa.Column('website', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=1500), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.PickleType(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website')
    op.drop_table('Show')
    # ### end Alembic commands ###