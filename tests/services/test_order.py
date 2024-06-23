from dataclasses import dataclass
from typing import Generic, SupportsAbs, TypeVar
import pytest

from app.repositories.err import EntityNotFoundError
from app.repositories.order import OrderRepositoryInterface, PostgresOrderRepository
from app.repositories.postgres import PostgresSession
from app.repositories.product import (
    PostgresProductRepository,
    ProductRepositoryInterface,
)
from app.repositories.session import RepositorySession
from app.repositories.user import PostgresUserRepository, UserRepositoryInterface
from app.services.order import OrderService
from tests.models.constructor import new_product, new_user

S = TypeVar("S", bound=SupportsAbs[RepositorySession])


@dataclass
class OrderServiceFixture(Generic[S]):
    order_service: OrderService[S]
    user_repository: UserRepositoryInterface[S]
    product_repository: ProductRepositoryInterface[S]
    order_repository: OrderRepositoryInterface[S]
    repository_session: S


@pytest.fixture
def order_service_fixture(postgres_session):
    user_repository = PostgresUserRepository()
    product_repository = PostgresProductRepository()
    order_repository = PostgresOrderRepository()
    order_service = OrderService(
        user_repository, product_repository, order_repository, postgres_session
    )
    return OrderServiceFixture(
        order_service,
        user_repository,
        product_repository,
        order_repository,
        postgres_session,
    )


def test_should_raise_entity_not_found_if_user_id_not_valid(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):
    product_repository = order_service_fixture.product_repository
    order_service = order_service_fixture.order_service
    session = order_service_fixture.repository_session

    product = new_product()
    with pytest.raises(EntityNotFoundError):
        with session:
            product_repository.save(product, session)
            session.commit()

        order_service.place_order("unknown", {product.id: 3})


def test_should_raise_entity_not_found_if_product_id_not_valid(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):
    user_repository = order_service_fixture.user_repository
    order_service = order_service_fixture.order_service
    session = order_service_fixture.repository_session

    user = new_user()
    with pytest.raises(EntityNotFoundError):
        with session:
            user_repository.save(user, session)
            session.commit()

        order_service.place_order(user.id, {"unknown": 3})


def test_should_raise_error_if_purchase_quantity_is_not_greater_than_0(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):
    product_repository = order_service_fixture.product_repository
    user_repository = order_service_fixture.user_repository
    order_service = order_service_fixture.order_service
    session = order_service_fixture.repository_session

    product = new_product()
    user = new_user()

    with session:
        user_repository.save(user, session)
        product_repository.save(product, session)
        session.commit()

    with pytest.raises(ValueError) as exc_info:
        order_service.place_order(user.id, {product.id: 0})
    assert "purchasing quantity must be greater than 0" in str(exc_info.value)
