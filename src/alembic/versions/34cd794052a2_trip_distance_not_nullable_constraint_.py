"""trip_distance not nullable constraint added

Revision ID: 34cd794052a2
Revises: a985bc13939c
Create Date: 2023-12-22 12:53:32.246937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34cd794052a2'
down_revision: Union[str, None] = 'a985bc13939c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trips', 'trip_distance',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trips', 'trip_distance',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)
    # ### end Alembic commands ###