from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres import PostgresSession
from app.repositories.product import PostgresProductRepository
from app.repositories.user import PostgresUserRepository


def set_up_tables(session: PostgresSession):
    stmts = [
        PostgresProductRepository.CREATE_TABLE_IF_NOT_EXISTS,
        PostgresUserRepository.CREATE_TABLE_IF_NOT_EXISTS,
        PostgresOrderRepository.CREATE_TABLES_IF_NOT_EXISTS,
    ]

    with session.get_cursor() as cur:
        for stmt in stmts:
            cur.execute(stmt)


def drop_tables(session: PostgresSession):
    stmts = [
        PostgresProductRepository.DROP_TABLE,
        PostgresUserRepository.DROP_TABLE,
        PostgresOrderRepository.DROP_TABLES,
    ]

    with session.get_cursor() as cur:
        for stmt in stmts:
            cur.execute(stmt)
