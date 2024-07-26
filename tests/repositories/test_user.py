import pytest
from app.repositories.base import LockLevel
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres.session import PostgresSession
from app.repositories.user import (
    PostgresUserRepository,
)
from tests.models.constructor import new_user


def test_should_save_and_get_user(repository_session: PostgresSession):
    user = new_user()
    user_repository = PostgresUserRepository(repository_session.new_operator)
    with repository_session:
        user_repository.save(user)
        assert user == user_repository.get_by_id(user.id)


def test_should_raise_not_found_if_user_id_not_exist(
    repository_session: PostgresSession,
):
    user_repository = PostgresUserRepository(repository_session.new_operator)

    with repository_session:
        with pytest.raises(EntityNotFoundError) as exc_info:
            user_repository.get_by_id("unknown")
    assert str(exc_info.value) == EntityNotFoundError.format_err_msg(
        "user_id", "unknown"
    )


def test_should_save_able_to_update_user(repository_session: PostgresSession):
    user = new_user(balance=99)
    user_repository = PostgresUserRepository(repository_session.new_operator)
    with repository_session:
        user_repository.save(user)

        user.balance = 1
        user_repository.save(user)

        assert user_repository.get_by_id(user.id).balance == 1
