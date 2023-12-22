from pydantic import BaseModel

from .env import (
    TAXI_DB_HOST,
    TAXI_DB_NAME,
    TAXI_DB_PASSWORD,
    TAXI_DB_PORT,
    TAXI_DB_USER,
)


class PostgresCredentials(BaseModel):
    host: str
    port: int
    db: str
    user: str
    password: str

    def get_postgres_uri(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


taxi_db_creds = PostgresCredentials(
    host=TAXI_DB_HOST,
    port=TAXI_DB_PORT,
    db=TAXI_DB_NAME,
    user=TAXI_DB_USER,
    password=TAXI_DB_PASSWORD,
)
