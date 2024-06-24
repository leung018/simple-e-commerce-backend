from typing import Generator
import pytest

from app.repositories.migration import drop_tables, set_up_tables
from app.repositories.postgres import PostgresSession, new_postgres_config_from_env


@pytest.fixture
def postgres_session() -> Generator[PostgresSession, None, None]:
    session = PostgresSession(new_postgres_config_from_env())
    with session:
        set_up_tables(session)
        session.commit()
    yield session
    with session:
        drop_tables(session)
        session.commit()
