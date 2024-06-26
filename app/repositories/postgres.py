from dataclasses import dataclass
import os
import psycopg

from app.repositories.session import RepositorySession


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


class PostgresSession(RepositorySession):
    def __init__(self, config: PostgresConfig):
        self._config = config

    def __enter__(self):
        self._conn = self._new_postgres_conn()
        self._conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._conn.close()

    def _new_postgres_conn(self):
        return psycopg.connect(
            host=self._config.host,
            user=self._config.user,
            password=self._config.password,
            dbname=self._config.database,
            port=self._config.port,
        )

    def get_operator(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
