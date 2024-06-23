from dataclasses import dataclass
import os
import psycopg

from app.repositories.session import RepositorySession


@dataclass(frozen=True)
class PostgresContext:
    host: str
    port: int
    user: str
    password: str
    database: str


def new_postgres_context_from_env() -> PostgresContext:
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    database = os.getenv("POSTGRES_DB", "db")
    return PostgresContext(
        host=host, port=port, user=user, password=password, database=database
    )


class PostgresSession(RepositorySession):
    def __init__(self, context: PostgresContext):
        self._context = context

    def __enter__(self):
        self._conn = self._new_postgres_conn()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._conn.close()

    def _new_postgres_conn(self):
        return psycopg.connect(
            host=self._context.host,
            user=self._context.user,
            password=self._context.password,
            dbname=self._context.database,
            port=self._context.port,
        )

    def get_cursor(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
