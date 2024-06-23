from dataclasses import dataclass
from typing import Generic, SupportsAbs, TypeVar
import pytest

from app.repositories.err import EntityNotFoundError
from app.repositories.order import OrderRepositoryInterface, PostgresOrderRepository
from app.repositories.product import (
    PostgresProductRepository,
    ProductRepositoryInterface,
)
from app.repositories.session import RepositorySession
from app.repositories.user import PostgresUserRepository, UserRepositoryInterface
from app.services.order import OrderService
from tests.models.constructor import new_product

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
    order_service_fixture: OrderServiceFixture,
):
    product_repository = order_service_fixture.product_repository
    order_service = order_service_fixture.order_service
    session = order_service_fixture.repository_session

    product = new_product()
    with session:
        with pytest.raises(EntityNotFoundError):
            product_repository.save(product, session)
            order_service.place_order("unknown", {product.id: 3})
