from app.repositories.auth import PostgresAuthRecordRepository
from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres import (
    PostgresConfig,
    PostgresSession,
)
from app.repositories.product import PostgresProductRepository
from app.repositories.user import PostgresUserRepository


def get_repository_session():
    return PostgresSession(PostgresConfig.from_env())


def get_order_repository():
    return PostgresOrderRepository()


def get_user_repository():
    return PostgresUserRepository()


def get_product_repository():
    return PostgresProductRepository()


def get_auth_record_repository():
    return PostgresAuthRecordRepository()
