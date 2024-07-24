from typing import Generator
import pytest

from app.dependencies import get_repository_session
from app.repositories.migration import migrate_down, migrate_up
from app.repositories.postgres import PostgresSession


@pytest.fixture
def repository_session() -> Generator[PostgresSession, None, None]:
    session = get_repository_session()
    migrate_up(session)
    yield session
    migrate_down(session)
