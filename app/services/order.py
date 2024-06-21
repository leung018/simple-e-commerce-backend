from typing import Dict
from app.repositories.order import OrderRepositoryInterface
from app.repositories.product import ProductRepositoryInterface
from app.repositories.user import UserRepositoryInterface


class OrderService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        product_repository: ProductRepositoryInterface,
        order_repository: OrderRepositoryInterface,
    ):
        pass

    def place_order(self, user_id: str, product_id_to_quantity: Dict[str, int]):
        pass
