import pytest
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.user import (
    PostgresUserRepository,
)
from tests.models.constructor import new_user


def test_should_save_and_get_user(repository_session: PostgresSession):
    user = new_user()
    user_repository = PostgresUserRepository()
    with repository_session:
        user_repository.save(user, repository_session)
        assert user == user_repository.get_by_id(user.id, repository_session)


def test_should_raise_not_found_if_user_id_not_exist(
    repository_session: PostgresSession,
):
    user_repository = PostgresUserRepository()

    with repository_session:
        with pytest.raises(EntityNotFoundError):
            user_repository.get_by_id("unknown", repository_session)


def test_should_save_able_to_update_user(repository_session: PostgresSession):
    user = new_user(balance=99)
    user_repository = PostgresUserRepository()
    with repository_session:
        user_repository.save(user, repository_session)

        user.balance = 1
        user_repository.save(user, repository_session)

        assert user_repository.get_by_id(user.id, repository_session).balance == 1
