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


def new_postgres_conn(postgres_context: PostgresContext):
    return psycopg.connect(
        host=postgres_context.host,
        user=postgres_context.user,
        password=postgres_context.password,
        dbname=postgres_context.database,
        port=postgres_context.port,
    )


class PostgresSession(RepositorySession):
    def __init__(self):
        self.conn = new_postgres_conn(new_postgres_context_from_env())

    def commit(self):
        self.conn.commit()
