from app.repositories.auth import PostgresAuthRecordRepository
from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres.session import PostgresSession
from app.repositories.product import PostgresProductRepository
from app.repositories.user import PostgresUserRepository


def migrate_up(session: PostgresSession):
    stmts = [
        PostgresProductRepository.CREATE_TABLE_IF_NOT_EXISTS,
        PostgresUserRepository.CREATE_TABLE_IF_NOT_EXISTS,
        PostgresOrderRepository.CREATE_TABLES_IF_NOT_EXISTS,
        PostgresAuthRecordRepository.CREATE_TABLE_IF_NOT_EXISTS,
    ]

    with session:
        with session.new_operator() as cur:
            for stmt in stmts:
                cur.execute(stmt)
        session.commit()


def migrate_down(session: PostgresSession):
    stmts = [
        PostgresProductRepository.DROP_TABLE,
        PostgresUserRepository.DROP_TABLE,
        PostgresOrderRepository.DROP_TABLES,
        PostgresAuthRecordRepository.DROP_TABLE,
    ]

    with session:
        with session.new_operator() as cur:
            for stmt in stmts:
                cur.execute(stmt)
        session.commit()
