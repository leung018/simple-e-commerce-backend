from typing import Generic, TypeVar

from app.models.auth import AuthInput
from app.repositories.auth import AuthRecordRepositoryInterface
from app.repositories.session import RepositorySession
from app.repositories.user import UserRepositoryInterface

S = TypeVar("S", bound=RepositorySession)


class AuthService(Generic[S]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface[S],
        auth_repository: AuthRecordRepositoryInterface[S],
        repository_session: S,
    ):
        pass

    def register_user(self, auth_input: AuthInput):
        pass

    def get_access_token(self, auth_input: AuthInput) -> str:
        raise NotImplementedError

    def decode_user_id_from_token(self, token: str) -> str:
        raise NotImplementedError
