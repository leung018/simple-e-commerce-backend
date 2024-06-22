from abc import ABC, abstractmethod
from app.models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> User:
        pass
