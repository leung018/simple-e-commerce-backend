from abc import ABC, abstractmethod
from typing import List

from app.models.order import Order


class OrderRepositoryInterface(ABC):
    @abstractmethod
    def add(self, order: Order):
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> List[Order]:
        pass
