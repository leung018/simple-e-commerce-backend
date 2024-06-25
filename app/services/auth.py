from typing import Generic, TypeVar

from app.models.auth import AuthInput, AuthRecord
from app.models.user import USER_INITIAL_BALANCE, User
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
        self._user_repository = user_repository
        self._auth_repository = auth_repository
        self._session = repository_session

    def register_user(self, auth_input: AuthInput):
        with self._session:
            user = self._create_new_user()
            self._auth_repository.add(
                AuthRecord(
                    user_id=user.id,
                    hashed_password="TODO",
                    username=auth_input.username,
                ),
                self._session,
            )
            self._session.commit()

    def _create_new_user(self):
        user = User(id="TODO", balance=USER_INITIAL_BALANCE)
        self._user_repository.save(user, self._session)
        return user

    def get_access_token(self, auth_input: AuthInput) -> str:
        raise NotImplementedError

    def decode_user_id_from_token(self, token: str) -> str:
        raise NotImplementedError
