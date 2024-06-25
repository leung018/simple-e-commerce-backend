from typing import Generator
import pytest

from app.dependencies import get_repository_session
from app.repositories.migration import drop_tables, set_up_tables
from app.repositories.postgres import PostgresSession


@pytest.fixture
def repository_session() -> Generator[PostgresSession, None, None]:
    session = get_repository_session()
    set_up_tables(session)
    yield session
    drop_tables(session)
