from dataclasses import dataclass
import os


@dataclass(frozen=True)
class PostgresConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @staticmethod
    def from_env():
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        user = os.getenv("POSTGRES_USER", "admin")
        password = os.getenv("POSTGRES_PASSWORD", "password")
        database = os.getenv("POSTGRES_DB", "db")
        return PostgresConfig(
            host=host, port=port, user=user, password=password, database=database
        )
