from typing import Generator
import pytest

from app.models.user import User
from app.repositories.user import (
    PostgresUserRepository,
    UserRepositoryInterface,
)


@pytest.fixture
def user_repository() -> Generator[UserRepositoryInterface, None, None]:
    yield PostgresUserRepository()


def new_user(id="u1", balance=100.2):
    return User(id=id, balance=balance)


def test_should_save_and_get_user(user_repository: UserRepositoryInterface):
    user = new_user()
    user_repository.save(user)
    assert user == user_repository.get_by_id(user_id=user.id)
