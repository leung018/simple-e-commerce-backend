from typing import Generator
import pytest

from app.repositories.postgres import PostgresSession
from app.repositories.product import PostgresProductRepository


@pytest.fixture
def postgres_session() -> Generator[PostgresSession, None, None]:
    session = PostgresSession()
    with session.conn.cursor() as cur:
        cur.execute(PostgresProductRepository.CREATE_TABLE_IF_NOT_EXISTS)
    session.commit()
    yield session
    with session:
        with session.conn.cursor() as cur:
            cur.execute(PostgresProductRepository.DROP_TABLE)
    session.commit()
