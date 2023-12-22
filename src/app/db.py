from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from creds import taxi_db_creds

engine = create_engine(taxi_db_creds.get_postgres_uri())
Session = sessionmaker(engine)
