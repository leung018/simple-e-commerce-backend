from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Callable, Generic, TypeVar

import jwt
import pytest

from app.models.auth import AuthInput
from app.models.user import USER_INITIAL_BALANCE
from app.repositories.auth import (
    AuthRecordRepository,
    auth_record_repository_factory,
)
from app.repositories.base import RepositorySession
from app.repositories.user import UserRepository, user_repository_factory
from app.services.auth import (
    AuthService,
    AuthServiceConfig,
    DecodeAccessTokenError,
    GetAccessTokenError,
    RegisterUserError,
)
from tests.models.constructor import new_auth_input


Operator = TypeVar("Operator")


@dataclass
class AuthServiceFixture(Generic[Operator]):
    user_repository: UserRepository[Operator]
    auth_record_repository: AuthRecordRepository[Operator]
    auth_service_config: AuthServiceConfig
    auth_service_factory: Callable[[AuthServiceConfig], AuthService[Operator]]
    session: RepositorySession[Operator]

    def sign_up(self, auth_input: AuthInput):
        auth_service = self.auth_service_factory(self.auth_service_config)
        auth_service.sign_up(auth_input)

    def get_access_token(self, auth_input: AuthInput, expire_days: int = 7):
        auth_config = replace(
            self.auth_service_config, access_token_expire_days=expire_days
        )
        auth_service = self.auth_service_factory(auth_config)
        return auth_service.get_access_token(auth_input)

    def decode_user_id(self, access_token: str) -> str:
        auth_service = self.auth_service_factory(self.auth_service_config)
        return auth_service.decode_user_id(access_token)

    def get_user_by_username(self, username: str):
        with self.session:
            auth_record = self.auth_record_repository.get_by_username(username)
            return self.user_repository.get_by_id(auth_record.user_id)


@pytest.fixture
def auth_service_fixture(repository_session: RepositorySession):
    user_repository = user_repository_factory(repository_session.new_operator)
    auth_record_repository = auth_record_repository_factory(
        repository_session.new_operator
    )
    auth_service_config = AuthServiceConfig.from_env()

    def auth_service_factory(
        auth_service_config: AuthServiceConfig = auth_service_config,
    ):
        return AuthService(
            auth_service_config=auth_service_config,
            user_repository=user_repository,
            auth_repository=auth_record_repository,
            repository_session=repository_session,
        )

    return AuthServiceFixture(
        user_repository,
        auth_record_repository,
        auth_service_config,
        auth_service_factory,
        repository_session,
    )


def test_should_register_user_create_new_user_with_initial_balance(
    auth_service_fixture: AuthServiceFixture,
):
    auth_service_fixture.sign_up(new_auth_input(username="uname"))
    assert (
        auth_service_fixture.get_user_by_username("uname").balance
        == USER_INITIAL_BALANCE
    )


def test_should_not_allow_register_user_with_existing_username(
    auth_service_fixture: AuthServiceFixture,
):
    auth_service_fixture.sign_up(new_auth_input(username="uname"))
    with pytest.raises(RegisterUserError) as exc_info:
        auth_service_fixture.sign_up(new_auth_input(username="uname"))
    assert "username: uname already exists" == str(exc_info.value)

    # using different username can be success
    auth_service_fixture.sign_up(new_auth_input(username="uname2"))


def test_should_not_able_to_get_access_token_if_username_or_password_not_match(
    auth_service_fixture: AuthServiceFixture,
):
    auth_service_fixture.sign_up(new_auth_input(username="uname", password="password"))

    with pytest.raises(GetAccessTokenError) as exc_info:
        auth_service_fixture.get_access_token(
            new_auth_input(username="unaem", password="password")
        )
    assert "username or password is not correct" == str(exc_info.value)

    with pytest.raises(GetAccessTokenError) as exc_info:
        auth_service_fixture.get_access_token(
            new_auth_input(username="uname", password="passwodr")
        )
    assert "username or password is not correct" == str(exc_info.value)


def test_should_able_to_decode_user_id(
    auth_service_fixture: AuthServiceFixture,
):
    auth_input = new_auth_input(username="uname")
    auth_service_fixture.sign_up(auth_input)

    token = auth_service_fixture.get_access_token(auth_input)
    user_id = auth_service_fixture.decode_user_id(token)

    assert auth_service_fixture.get_user_by_username("uname").id == user_id


def test_should_set_expire_time_of_access_token(
    auth_service_fixture: AuthServiceFixture,
):
    auth_input = new_auth_input()
    auth_service_fixture.sign_up(auth_input)
    token = auth_service_fixture.get_access_token(auth_input, expire_days=1)
    decoded_token = jwt.decode(token, options={"verify_signature": False})

    token_expiry = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
    expected_expiry = datetime.now(timezone.utc) + timedelta(days=1)

    tolerance = timedelta(minutes=1)
    assert abs(token_expiry - expected_expiry) <= tolerance


def test_should_raise_exception_if_decode_an_expired_token(
    auth_service_fixture: AuthServiceFixture,
):
    auth_input = new_auth_input()
    auth_service_fixture.sign_up(auth_input)
    token = auth_service_fixture.get_access_token(auth_input, expire_days=-1)

    with pytest.raises(DecodeAccessTokenError):
        auth_service_fixture.decode_user_id(token)
