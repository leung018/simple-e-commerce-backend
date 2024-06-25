from dataclasses import dataclass
from typing import Generic, TypeVar

import pytest

from app.dependencies import get_auth_record_repository, get_user_repository
from app.models.auth import AuthInput
from app.models.user import USER_INITIAL_BALANCE
from app.repositories.auth import AuthRecordRepositoryInterface
from app.repositories.session import RepositorySession
from app.repositories.user import UserRepositoryInterface
from app.services.auth import AuthService
from tests.models.constructor import new_auth_input


S = TypeVar("S", bound=RepositorySession)


@dataclass
class AuthServiceFixture(Generic[S]):
    user_repository: UserRepositoryInterface[S]
    auth_record_repository: AuthRecordRepositoryInterface[S]
    auth_service: AuthService[S]
    session: S

    def register_user(self, auth_input: AuthInput):
        self.auth_service.register_user(auth_input)

    def get_user_by_username(self, username: str):
        with self.session:
            auth_record = self.auth_record_repository.get_by_username(
                username, self.session
            )
            return self.user_repository.get_by_id(auth_record.user_id, self.session)


@pytest.fixture
def auth_service_fixture(repository_session):
    user_repository = get_user_repository()
    auth_record_repository = get_auth_record_repository()
    auth_service = AuthService(
        user_repository=user_repository,
        auth_repository=auth_record_repository,
        repository_session=repository_session,
    )
    return AuthServiceFixture(
        user_repository, auth_record_repository, auth_service, repository_session
    )


def test_should_register_user_create_new_user_with_initial_balance(
    auth_service_fixture: AuthServiceFixture,
):
    auth_service_fixture.register_user(new_auth_input(username="uname"))
    assert (
        auth_service_fixture.get_user_by_username("uname").balance
        == USER_INITIAL_BALANCE
    )
