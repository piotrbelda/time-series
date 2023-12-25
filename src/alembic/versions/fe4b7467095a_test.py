"""test

Revision ID: fe4b7467095a
Revises: 
Create Date: 2023-12-25 13:56:28.770170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe4b7467095a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('trips',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=True),
    sa.Column('tpep_pickup', sa.DateTime(), nullable=False),
    sa.Column('tpep_dropoff', sa.DateTime(), nullable=False),
    sa.Column('passenger_count', sa.SmallInteger(), nullable=True),
    sa.Column('trip_distance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('rate_code_id', sa.Integer(), nullable=True),
    sa.Column('store_and_fwd_flag', sa.Boolean(), nullable=True),
    sa.Column('pu_location_id', sa.Integer(), nullable=True),
    sa.Column('do_location_id', sa.Integer(), nullable=True),
    sa.Column('payment_type', sa.Integer(), nullable=True),
    sa.Column('fare_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('extra', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('tip_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.PrimaryKeyConstraint('id', 'tpep_pickup'),
    postgresql_partition_by='RANGE (tpep_pickup)'
    )


def downgrade() -> None:
    op.drop_table('trips')
