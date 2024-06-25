from typing import TypeVar, Generic
from uuid import uuid4
from app.err import MyValueError
from app.models.order import Order, OrderItem, PurchaseInfo
from app.models.product import Product
from app.models.user import User
from app.repositories.order import OrderRepositoryInterface
from app.repositories.product import ProductRepositoryInterface
from app.repositories.session import RepositorySession
from app.repositories.user import UserRepositoryInterface

S = TypeVar("S", bound=RepositorySession)

_QUANTITY_NOT_POSITIVE_ERROR_MSG = "purchasing quantity must be greater than 0"


class PlaceOrderError(MyValueError):
    pass


class OrderService(Generic[S]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface[S],
        product_repository: ProductRepositoryInterface[S],
        order_repository: OrderRepositoryInterface[S],
        repository_session: S,
    ):
        self._user_repository = user_repository
        self._product_repository = product_repository
        self._order_repository = order_repository
        self._session = repository_session

    def place_order(self, user_id: str, product_id_to_quantity: dict[str, int]):
        self._validate_quantities(product_id_to_quantity)

        with self._session:
            user = self._fetch_user(user_id)
            total_price = self._process_products(product_id_to_quantity)
            self._make_payment(user, total_price)
            self._record_order(user.id, product_id_to_quantity)

            self._session.commit()

    def _validate_quantities(self, product_id_to_quantity: dict[str, int]):
        if not product_id_to_quantity:
            raise PlaceOrderError(_QUANTITY_NOT_POSITIVE_ERROR_MSG)

        for _, quantity in product_id_to_quantity.items():
            if quantity <= 0:
                raise PlaceOrderError(_QUANTITY_NOT_POSITIVE_ERROR_MSG)

    def _fetch_user(self, user_id):
        return self._user_repository.get_by_id(user_id, self._session)

    def _process_products(self, product_id_to_quantity: dict[str, int]) -> float:
        """
        Return total price of this order
        """

        total_price: float = 0
        for product_id in product_id_to_quantity:
            product = self._product_repository.get_by_id(product_id, self._session)
            purchase_quantity = product_id_to_quantity[product_id]

            self._update_product_inventory(product, purchase_quantity)
            total_price += purchase_quantity * product.price
        return total_price

    def _update_product_inventory(self, product: Product, purchase_quantity: int):
        if product.quantity < purchase_quantity:
            raise PlaceOrderError("quantity of product is not enough for your purchase")

        product.quantity -= purchase_quantity
        self._product_repository.save(product, self._session)

    def _make_payment(self, user: User, total_price: float):
        if total_price > user.balance:
            raise PlaceOrderError("not enough balance")

        user.balance -= total_price
        self._user_repository.save(user, self._session)

    def _record_order(self, user_id: str, product_id_to_quantity: dict[str, int]):
        order = Order.create(
            id=str(uuid4()),
            user_id=user_id,
            order_items=tuple(
                OrderItem(product_id, quantity)
                for product_id, quantity, in product_id_to_quantity.items()
            ),
        )
        self._order_repository.add(order, self._session)
