"""added about me and last seen to user model

Revision ID: 425524a8e7c6
Revises: f7d37c712e9c
Create Date: 2020-07-06 17:13:35.590545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '425524a8e7c6'
down_revision = 'f7d37c712e9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###
