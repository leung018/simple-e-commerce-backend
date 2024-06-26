from app.repositories.postgres import (
    PostgresConfig,
    PostgresSession,
)


def get_repository_session():
    return PostgresSession(PostgresConfig.from_env())
