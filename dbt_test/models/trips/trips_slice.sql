-- {{ config(materialized='table') }}
with trips_slice as (
    select
        vendor_id,
        tpep_pickup,
        tpep_dropoff
    from trips
)
select * from trips_slice
