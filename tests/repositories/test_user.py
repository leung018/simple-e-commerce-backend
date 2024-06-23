import pytest
from app.models.user import User
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.user import (
    PostgresUserRepository,
)


def new_user(id="u1", balance=100.2):
    return User(id=id, balance=balance)


def test_should_save_and_get_user(postgres_session: PostgresSession):
    user = new_user()
    user_repository = PostgresUserRepository()
    with postgres_session:
        user_repository.save(user, postgres_session)
        postgres_session.commit()
    assert user == user_repository.get_by_id(user.id, postgres_session)


def test_should_raise_not_found_if_user_id_not_exist(
    postgres_session: PostgresSession,
):
    user_repository = PostgresUserRepository()

    with pytest.raises(EntityNotFoundError):
        user_repository.get_by_id("unknown", postgres_session)
