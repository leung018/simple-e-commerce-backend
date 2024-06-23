from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar, SupportsAbs

from app.models.order import Order
from app.repositories.session import RepositorySession

S = TypeVar("S", bound=SupportsAbs[RepositorySession])


class OrderRepositoryInterface(ABC, Generic[S]):
    @abstractmethod
    def add(self, order: Order, session: S):
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: str, session: S) -> List[Order]:
        pass
