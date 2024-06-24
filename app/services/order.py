from typing import Dict, TypeVar, Generic
from app.err import MyValueError
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

    def place_order(self, user_id: str, product_id_to_quantity: Dict[str, int]):
        with self._session:
            user = self._user_repository.get_by_id(user_id, self._session)
            if not product_id_to_quantity:
                raise PlaceOrderError(_QUANTITY_NOT_POSITIVE_ERROR_MSG)

            total_price: float = 0
            for product_id in product_id_to_quantity:
                product = self._product_repository.get_by_id(product_id, self._session)
                purchase_quantity = product_id_to_quantity[product_id]
                if purchase_quantity <= 0:
                    raise PlaceOrderError(_QUANTITY_NOT_POSITIVE_ERROR_MSG)
                if product.quantity < purchase_quantity:
                    raise PlaceOrderError(
                        "quantity of product is not enough for your purchase"
                    )
                total_price += purchase_quantity * product.price

                product.quantity -= purchase_quantity
                self._product_repository.save(product, self._session)

            if total_price > user.balance:
                raise PlaceOrderError("not enough balance")

            user.balance -= total_price
            self._user_repository.save(user, self._session)

            self._session.commit()
