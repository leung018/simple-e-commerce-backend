from dataclasses import dataclass
from typing import Dict, Generic, SupportsAbs, TypeVar
import pytest

from app.err import MyValueError
from app.models.product import Product
from app.models.user import User
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
    session: S

    def save_user(self, user):
        with self.session:
            self.user_repository.save(user, self.session)
            self.session.commit()

    def save_products(self, products):
        with self.session:
            for product in products:
                self.product_repository.save(product, self.session)
            self.session.commit()

    def place_order(self, user_id, product_id_to_quantity: Dict[str, int]):
        self.order_service.place_order(user_id, product_id_to_quantity)


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
    product = new_product()
    order_service_fixture.save_products([product])

    with pytest.raises(EntityNotFoundError):
        order_service_fixture.place_order("unknown_user_id", {product.id: 3})


def test_should_raise_entity_not_found_if_product_id_not_valid(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):
    user = new_user()
    order_service_fixture.save_user(user)

    with pytest.raises(EntityNotFoundError):
        order_service_fixture.place_order(user.id, {"unknown_product_id": 3})


def test_should_raise_error_if_total_purchase_quantity_is_not_greater_than_0(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):
    product1 = new_product(id="p1")
    product2 = new_product(id="p2")
    user = new_user()

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product1, product2])

    expected_msg = "purchasing quantity must be greater than 0"
    with pytest.raises(MyValueError) as exc_info:
        order_service_fixture.place_order(user.id, {"p1": 0, "p2": 2})
    assert expected_msg in str(exc_info.value)

    with pytest.raises(MyValueError) as exc_info:
        order_service_fixture.place_order(user.id, {})
    assert expected_msg in str(exc_info.value)


def test_should_raise_error_if_purchase_quantity_is_less_than_product_quantity(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):

    product = new_product(quantity=5, price=1)
    user = new_user(balance=1000)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product])

    with pytest.raises(MyValueError) as exc_info:
        order_service_fixture.place_order(user.id, {product.id: 6})
    assert "quantity of product is not enough for your purchase" in str(exc_info.value)


def test_should_raise_error_if_user_balance_is_not_enough_to_buy(
    order_service_fixture: OrderServiceFixture[RepositorySession],
):
    product1 = new_product("p1", quantity=99, price=2)
    product2 = new_product("p2", quantity=99, price=3)
    user = new_user(balance=18.9)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product1, product2])

    with pytest.raises(MyValueError) as exc_info:
        order_service_fixture.place_order(user.id, {"p1": 2, "p2": 5})  # 2*2 + 3*5 = 19
    assert "not enough balance" in str(exc_info.value)
