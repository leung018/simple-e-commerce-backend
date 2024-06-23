from typing import Dict, SupportsAbs, TypeVar, Generic
from app.models.order import Order
from app.repositories.order import OrderRepositoryInterface
from app.repositories.product import ProductRepositoryInterface
from app.repositories.session import RepositorySession
from app.repositories.user import UserRepositoryInterface

S = TypeVar("S", bound=SupportsAbs[RepositorySession])


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

            for product_id in product_id_to_quantity:
                product = self._product_repository.get_by_id(product_id, self._session)
                quantity = product_id_to_quantity[product_id]
                if quantity <= 0:
                    raise ValueError("purchasing quantity must be greater than 0")
