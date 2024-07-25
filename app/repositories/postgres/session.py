import psycopg
from app.repositories.base import RepositorySession
from app.repositories.postgres.config import PostgresConfig


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

    def new_operator(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
