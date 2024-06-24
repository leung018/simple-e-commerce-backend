from dataclasses import dataclass
from typing import Dict, Generic, Optional, TypeVar
import pytest

from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.repositories.order import OrderRepositoryInterface, PostgresOrderRepository
from app.repositories.product import (
    PostgresProductRepository,
    ProductRepositoryInterface,
)
from app.repositories.session import RepositorySession
from app.repositories.user import PostgresUserRepository, UserRepositoryInterface
from app.services.order import OrderService, PlaceOrderError
from tests.models.constructor import new_product, new_user

S = TypeVar("S", bound=RepositorySession)


@dataclass
class OrderServiceFixture(Generic[S]):
    order_service: OrderService[S]
    user_repository: UserRepositoryInterface[S]
    product_repository: ProductRepositoryInterface[S]
    order_repository: OrderRepositoryInterface[S]
    session: S

    def save_user(self, user: User):
        with self.session:
            self.user_repository.save(user, self.session)
            self.session.commit()

    def save_products(self, products: list[Product]):
        with self.session:
            for product in products:
                self.product_repository.save(product, self.session)
            self.session.commit()

    def place_order(self, user_id, product_id_to_quantity: Dict[str, int]):
        self.order_service.place_order(user_id, product_id_to_quantity)

    def get_user(self, user_id):
        with self.session:
            return self.user_repository.get_by_id(user_id, self.session)

    def get_products(self, product_ids: list[str]):
        with self.session:
            products = [
                self.product_repository.get_by_id(product_id, self.session)
                for product_id in product_ids
            ]
            return products

    def get_most_recent_order(self, user_id: str) -> Optional[Order]:
        with self.session:
            orders = self.order_repository.get_by_user_id(user_id, self.session)
            if not orders:
                return None
            return orders[0]

    def assert_place_order_error(
        self, user_id, product_id_to_quantity: Dict[str, int], expected_err_msg: str
    ):
        product_ids = list(product_id_to_quantity.keys())

        def fetch_user_products_and_order():
            user = self.get_user(user_id)
            products = self.get_products(product_ids)
            order_or_none = self.get_most_recent_order(user_id)
            return (user, products, order_or_none)

        original_tuples = fetch_user_products_and_order()

        with pytest.raises(PlaceOrderError) as exc_info:
            self.place_order(user_id, product_id_to_quantity)

        assert expected_err_msg == str(exc_info.value)

        # make sure no side effects:
        new_tuples = fetch_user_products_and_order()
        assert original_tuples == new_tuples


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


def test_should_raise_error_if_total_purchase_quantity_is_not_greater_than_0(
    order_service_fixture: OrderServiceFixture,
):
    product1 = new_product(id="p1")
    product2 = new_product(id="p2")
    user = new_user()

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product1, product2])

    expected_err_msg = "purchasing quantity must be greater than 0"

    order_service_fixture.assert_place_order_error(
        user.id, {"p1": 0, "p2": 2}, expected_err_msg
    )
    order_service_fixture.assert_place_order_error(user.id, {}, expected_err_msg)


def test_should_raise_error_if_purchase_quantity_is_less_than_product_quantity(
    order_service_fixture: OrderServiceFixture,
):

    product = new_product(quantity=5, price=1)
    user = new_user(balance=1000)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product])

    order_service_fixture.assert_place_order_error(
        user.id, {product.id: 6}, "quantity of product is not enough for your purchase"
    )


def test_should_raise_error_if_user_balance_is_not_enough_to_buy(
    order_service_fixture: OrderServiceFixture,
):
    product1 = new_product("p1", quantity=99, price=2)
    product2 = new_product("p2", quantity=99, price=3)
    # total price: 2*2 + 3*5 = 19

    user = new_user(balance=18.9)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product1, product2])

    order_service_fixture.assert_place_order_error(
        user.id, {"p1": 2, "p2": 5}, "not enough balance"
    )


def test_should_make_order_successfully_if_balance_is_enough_to_buy(
    order_service_fixture: OrderServiceFixture,
):
    product1 = new_product("p1", quantity=50, price=2)
    product2 = new_product("p2", quantity=30, price=3)
    # total price: 2*2 + 3*5 = 19

    user = new_user(balance=19)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product1, product2])

    order_service_fixture.place_order(user.id, {"p1": 2, "p2": 5})

    # Check user balance
    assert order_service_fixture.get_user(user.id).balance == 0

    # Check product quantities
    [new_product1, new_product2] = order_service_fixture.get_products(
        [product1.id, product2.id]
    )
    assert new_product1.quantity == 48
    assert new_product2.quantity == 25

    # Check order is made
    order = order_service_fixture.get_most_recent_order(user.id)
    assert order is not None
    assert order.user_id == user.id
    assert order.product_ids == frozenset([product1.id, product2.id])


def test_should_order_id_generated_are_different_each_time(
    order_service_fixture: OrderServiceFixture,
):
    product = new_product(quantity=10, price=1)
    user = new_user(balance=100)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product])

    order_service_fixture.place_order(user.id, {product.id: 1})
    order1 = order_service_fixture.get_most_recent_order(user.id)

    order_service_fixture.place_order(user.id, {product.id: 1})
    order2 = order_service_fixture.get_most_recent_order(user.id)

    assert order1 is not None and order2 is not None
    assert order1.id != order2.id
