from typing import Generator
import pytest

from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres import PostgresSession, new_postgres_context_from_env
from app.repositories.product import PostgresProductRepository
from app.repositories.user import PostgresUserRepository


@pytest.fixture
def postgres_session() -> Generator[PostgresSession, None, None]:
    session = PostgresSession(new_postgres_context_from_env())
    with session.conn.cursor() as cur:
        cur.execute(PostgresProductRepository.CREATE_TABLE_IF_NOT_EXISTS)
        cur.execute(PostgresUserRepository.CREATE_TABLE_IF_NOT_EXISTS)
        cur.execute(PostgresOrderRepository.CREATE_TABLES_IF_NOT_EXISTS)
    session.commit()
    yield session
    with session:
        with session.conn.cursor() as cur:
            cur.execute(PostgresProductRepository.DROP_TABLE)
            cur.execute(PostgresUserRepository.DROP_TABLE)
            cur.execute(PostgresOrderRepository.DROP_TABLES)
    session.commit()
