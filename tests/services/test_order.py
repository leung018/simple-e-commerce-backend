from dataclasses import dataclass
from threading import Thread
from typing import Generic, Optional, TypeVar
from uuid import UUID, uuid4
import pytest

from app.dependencies import get_repository_session
from app.models.order import Order, OrderItem, PurchaseInfo
from app.models.product import Product
from app.models.user import User
from app.repositories.order import OrderRepository, order_repository_factory
from app.repositories.product import (
    ProductRepository,
    product_repository_factory,
)
from app.repositories.base import RepositorySession
from app.repositories.user import UserRepository, user_repository_factory
from app.services.order import OrderService, PlaceOrderError
from tests.models.constructor import new_product, new_user

Operator = TypeVar("Operator")


@dataclass
class OrderServiceFixture(Generic[Operator]):
    order_service: OrderService[Operator]
    user_repository: UserRepository[Operator]
    product_repository: ProductRepository[Operator]
    order_repository: OrderRepository[Operator]
    session: RepositorySession[Operator]

    def save_user(self, user: User):
        with self.session:
            self.user_repository.save(user)
            self.session.commit()

    def save_products(self, products: list[Product]):
        with self.session:
            for product in products:
                self.product_repository.save(product)
            self.session.commit()

    def place_order(
        self, user_id, product_id_to_quantity: dict[str, int], order_id="dummy_id"
    ):
        order_items = tuple(
            OrderItem(product_id, quantity)
            for product_id, quantity, in product_id_to_quantity.items()
        )
        self.order_service.place_order(user_id, PurchaseInfo(order_items, order_id))

    def get_user(self, user_id):
        with self.session:
            return self.user_repository.get_by_id(user_id)

    def get_products(self, product_ids: list[str]):
        with self.session:
            products = [
                self.product_repository.get_by_id(product_id)
                for product_id in product_ids
            ]
            return products

    def get_most_recent_order(self, user_id: str) -> Optional[Order]:
        with self.session:
            orders = self.order_repository.get_by_user_id(user_id)
            if not orders:
                return None
            return orders[0]

    def assert_place_order_error(
        self,
        user_id,
        product_id_to_quantity: dict[str, int],
        expected_err_msg: str,
        order_id: str = "dummy_id",
    ):
        product_ids = list(product_id_to_quantity.keys())

        def fetch_user_products_and_order():
            user = self.get_user(user_id)
            products = self.get_products(product_ids)
            order_or_none = self.get_most_recent_order(user_id)
            return (user, products, order_or_none)

        original_tuples = fetch_user_products_and_order()

        with pytest.raises(PlaceOrderError) as exc_info:
            self.place_order(user_id, product_id_to_quantity, order_id)

        assert expected_err_msg == str(exc_info.value)

        # make sure no side effects:
        new_tuples = fetch_user_products_and_order()
        assert original_tuples == new_tuples


@pytest.fixture
def order_service_fixture(repository_session: RepositorySession):
    order_service = OrderService(
        user_repository_factory,
        product_repository_factory,
        order_repository_factory,
        repository_session,
    )
    return OrderServiceFixture(
        order_service,
        user_repository_factory(repository_session.new_operator),
        product_repository_factory(repository_session.new_operator),
        order_repository_factory(repository_session.new_operator),
        repository_session,
    )


def test_should_raise_error_if_purchase_quantity_is_larger_than_product_quantity(
    order_service_fixture: OrderServiceFixture,
):

    product = new_product(quantity=5, price=1)
    user = new_user(balance=1000)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product])

    order_service_fixture.assert_place_order_error(
        user.id,
        {product.id: 6},
        expected_err_msg=PlaceOrderError.QUANTITY_NOT_ENOUGH_ERR_MSG,
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
        user.id,
        {"p1": 2, "p2": 5},
        expected_err_msg=PlaceOrderError.BALANCE_NOT_ENOUGH_ERR_MSG,
    )


def test_should_make_order_successfully_if_input_valid(
    order_service_fixture: OrderServiceFixture,
):
    product1 = new_product("p1", quantity=50, price=2)
    product2 = new_product("p2", quantity=30, price=3)
    # total price: 2*2 + 3*5 = 19

    user = new_user(balance=19)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product1, product2])

    order_service_fixture.place_order(user.id, {"p1": 2, "p2": 5}, "o1")

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
    assert order.id == "o1"
    assert order.user_id == user.id
    assert order.order_items == (OrderItem("p1", 2), OrderItem("p2", 5))


def test_should_prevent_placing_same_order_twice(
    order_service_fixture: OrderServiceFixture,
):
    product = new_product("p1", quantity=50, price=2)

    user = new_user(balance=38)

    order_service_fixture.save_user(user)
    order_service_fixture.save_products([product])

    order_service_fixture.place_order(user.id, {"p1": 2}, "o1")
    order_service_fixture.assert_place_order_error(
        user.id,
        {"p1": 3},
        order_id="o1",
        expected_err_msg=PlaceOrderError.ORDER_ALREADY_EXISTS_ERR_MSG,
    )


def test_should_prevent_race_condition_when_placing_orders(
    repository_session: RepositorySession,
):
    user_repository = user_repository_factory(repository_session.new_operator)
    product_repository = product_repository_factory(repository_session.new_operator)

    user1 = new_user(id="u1", balance=100)
    user2 = new_user(id="u2", balance=120)
    product1 = new_product(id="p1", quantity=12, price=5)
    product2 = new_product(id="p2", quantity=12, price=4)

    with repository_session:
        user_repository.save(user1)
        user_repository.save(user2)
        product_repository.save(product1)
        product_repository.save(product2)
        repository_session.commit()

    def place_order(user_id: str, order_items: tuple[OrderItem, ...]):
        order_service = OrderService(
            user_repository_factory,
            product_repository_factory,
            order_repository_factory,
            get_repository_session(),  # Same session cannot be shared between threads
        )
        purchase_info = PurchaseInfo(order_items, str(uuid4()))
        order_service.place_order(user_id, purchase_info)

    # They are the same but in different order. Make sure won't cause deadlock even in this case
    user1_order_items = (OrderItem("p1", 2), OrderItem("p2", 2))
    user2_order_items = (OrderItem("p2", 2), OrderItem("p1", 2))

    threads: list[Thread] = [
        Thread(
            target=place_order,
            args=(
                "u1",
                user1_order_items,
            ),
        ),
        Thread(
            target=place_order,
            args=(
                "u1",
                user1_order_items,
            ),
        ),
        Thread(
            target=place_order,
            args=(
                "u1",
                user1_order_items,
            ),
        ),
        Thread(
            target=place_order,
            args=(
                "u2",
                user2_order_items,
            ),
        ),
        Thread(
            target=place_order,
            args=(
                "u2",
                user2_order_items,
            ),
        ),
        Thread(
            target=place_order,
            args=(
                "u2",
                user2_order_items,
            ),
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    with repository_session:
        user1 = user_repository.get_by_id("u1")
        user2 = user_repository.get_by_id("u2")
        product1 = product_repository.get_by_id("p1")
        product2 = product_repository.get_by_id("p2")

        assert user1.balance == 46  # 100 - (2*5 + 2*4)*3
        assert user2.balance == 66  # 120 - (2*4 + 2*5)*3
        assert product1.quantity == 0
        assert product2.quantity == 0
