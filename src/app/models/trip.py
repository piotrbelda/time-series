from sqlalchemy import Column, Boolean, DateTime, Integer, Numeric, SmallInteger

from .base import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer)
    tpep_pickup = Column(DateTime, nullable=False)
    tpep_dropoff = Column(DateTime, nullable=False)
    passenger_count = Column(SmallInteger)
    trip_distance = Column(Numeric(10, 2), nullable=False)
    rate_code_id = Column(Integer)
    store_and_fwd_flag = Column(Boolean)
    pu_location_id = Column(Integer)
    do_location_id = Column(Integer)
    payment_type = Column(Integer)
    fare_amount = Column(Numeric(10,2))
    extra = Column(Numeric(10,2))
    tip_amount = Column(Numeric(10,2))
    total_amount = Column(Numeric(10,2))
