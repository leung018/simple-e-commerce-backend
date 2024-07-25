import pytest
from app.repositories.auth import PostgresAuthRecordRepository
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres.session import PostgresSession
from tests.models.constructor import new_auth_record


def test_should_add_auth_record_and_get_by_username(
    repository_session: PostgresSession,
):
    auth_record = new_auth_record()
    auth_record_repository = PostgresAuthRecordRepository(
        repository_session.new_operator
    )
    with repository_session:
        auth_record_repository.add(auth_record)
        assert auth_record == auth_record_repository.get_by_username(
            auth_record.username,
        )


def test_should_raise_entity_not_found_if_username_does_not_exists(
    repository_session: PostgresSession,
):
    auth_record_repository = PostgresAuthRecordRepository(
        repository_session.new_operator
    )
    with repository_session:
        with pytest.raises(EntityNotFoundError) as exc_info:
            auth_record_repository.get_by_username(
                "unknown",
            )
    assert str(exc_info.value) == EntityNotFoundError.format_err_msg(
        "username", "unknown"
    )
