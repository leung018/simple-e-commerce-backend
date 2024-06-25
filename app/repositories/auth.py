from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.models.auth import AuthRecord
from app.repositories.session import RepositorySession


S = TypeVar("S", bound=RepositorySession)


class AuthRecordRepositoryInterface(ABC, Generic[S]):
    @abstractmethod
    def add(self, auth_record: AuthRecord):
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> AuthRecord:
        """
        Raises:
            EntityNotFoundError: If no record is found with the provided username
        """
        pass
