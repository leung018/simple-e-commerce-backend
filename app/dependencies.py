from app.repositories.postgres.session import PostgresSession
from app.repositories.postgres.config import PostgresConfig


def get_repository_session():
    return PostgresSession(PostgresConfig.from_env())
