from typing import Dict, SupportsAbs, TypeVar, Generic
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
        pass

    def place_order(self, user_id: str, product_id_to_quantity: Dict[str, int]):
        pass
