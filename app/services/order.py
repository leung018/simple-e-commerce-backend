from typing import TypeVar, Generic
from uuid import uuid4
from app.err import MyValueError
from app.models.order import Order, PurchaseInfo
from app.models.product import Product
from app.models.user import User
from app.repositories.order import OrderRepository, OrderRepositoryFactory
from app.repositories.product import ProductRepository, ProductRepositoryFactory
from app.repositories.base import RepositorySession
from app.repositories.user import UserRepository, UserRepositoryFactory

Operator = TypeVar("Operator")


class PlaceOrderError(MyValueError):
    QUANTITY_NOT_ENOUGH_ERR_MSG = "quantity of product is not enough for your purchase"
    BALANCE_NOT_ENOUGH_ERR_MSG = "not enough balance"

    @classmethod
    def quantity_not_enough_error(cls):
        return PlaceOrderError(cls.QUANTITY_NOT_ENOUGH_ERR_MSG)

    @classmethod
    def balance_not_enough_error(cls):
        return PlaceOrderError(cls.BALANCE_NOT_ENOUGH_ERR_MSG)


class OrderService(Generic[Operator]):
    def __init__(
        self,
        user_repository_factory: UserRepositoryFactory[Operator],
        product_repository_factory: ProductRepositoryFactory[Operator],
        order_repository_factory: OrderRepositoryFactory[Operator],
        repository_session: RepositorySession[Operator],
    ):
        self._user_repository: UserRepository[Operator] = user_repository_factory(
            repository_session.new_operator
        )
        self._product_repository: ProductRepository[Operator] = (
            product_repository_factory(repository_session.new_operator)
        )
        self._order_repository: OrderRepository[Operator] = order_repository_factory(
            repository_session.new_operator
        )
        self._session = repository_session

    def place_order(self, user_id: str, purchase_info: PurchaseInfo):
        with self._session:
            user = self._user_repository.get_by_id(user_id, exclusive_lock=True)
            products_by_id = self._fetch_products_with_exclusive_lock(
                [item.product_id for item in purchase_info.order_items]
            )

            total_price = self._process_products(purchase_info, products_by_id)
            self._make_payment(user, total_price)
            self._record_order(user.id, purchase_info)

            self._session.commit()

    def _fetch_products_with_exclusive_lock(
        self, product_ids: list[str]
    ) -> dict[str, Product]:
        product_ids = sorted(
            product_ids
        )  # Consistent order of locking to avoid deadlocks

        products_by_id: dict[str, Product] = {}
        for product_id in product_ids:
            product = self._product_repository.get_by_id(
                product_id, exclusive_lock=True
            )
            products_by_id[product.id] = product
        return products_by_id

    def _process_products(
        self, purchase_info: PurchaseInfo, products_by_id: dict[str, Product]
    ) -> float:
        """
        Return total price of this order
        """

        total_price: float = 0
        for order_item in purchase_info.order_items:
            product = products_by_id[order_item.product_id]
            self._update_product_inventory(product, order_item.quantity)
            total_price += order_item.quantity * product.price
        return total_price

    def _update_product_inventory(self, product: Product, purchase_quantity: int):
        if product.quantity < purchase_quantity:
            raise PlaceOrderError.quantity_not_enough_error()

        product.quantity -= purchase_quantity
        self._product_repository.save(product)

    def _make_payment(self, user: User, total_price: float):
        if total_price > user.balance:
            raise PlaceOrderError.balance_not_enough_error()

        user.balance -= total_price
        self._user_repository.save(user)

    def _record_order(self, user_id: str, purchase_info: PurchaseInfo):
        order = Order(
            id=str(uuid4()),
            user_id=user_id,
            purchase_info=purchase_info,
        )
        self._order_repository.add(order)
