from typing import Dict, SupportsAbs, TypeVar, Generic
from app.err import MyValueError
from app.repositories.order import OrderRepositoryInterface
from app.repositories.product import ProductRepositoryInterface
from app.repositories.session import RepositorySession
from app.repositories.user import UserRepositoryInterface

S = TypeVar("S", bound=SupportsAbs[RepositorySession])

_QUANTITY_NOT_POSITIVE_ERROR_MSG = "purchasing quantity must be greater than 0"


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
                raise MyValueError(_QUANTITY_NOT_POSITIVE_ERROR_MSG)

            total_price = 0
            for product_id in product_id_to_quantity:
                product = self._product_repository.get_by_id(product_id, self._session)
                purchase_quantity = product_id_to_quantity[product_id]
                if purchase_quantity <= 0:
                    raise MyValueError(_QUANTITY_NOT_POSITIVE_ERROR_MSG)
                if product.quantity < purchase_quantity:
                    raise MyValueError(
                        "quantity of product is not enough for your purchase"
                    )
                total_price += purchase_quantity * product.price

            if total_price > user.balance:
                raise MyValueError("not enough balance")
