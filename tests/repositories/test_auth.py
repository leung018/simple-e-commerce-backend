import pytest
from app.repositories.auth import PostgresAuthRecordRepository
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from tests.models.constructor import new_auth_record


def test_should_add_auth_record_and_get_by_username(
    repository_session: PostgresSession,
):
    auth_record = new_auth_record()
    auth_record_repository = PostgresAuthRecordRepository()
    with repository_session:
        auth_record_repository.add(auth_record, repository_session)
        assert auth_record == auth_record_repository.get_by_username(
            auth_record.username, repository_session
        )


def test_should_raise_entity_not_found_if_username_does_not_exists(
    repository_session: PostgresSession,
):
    auth_record_repository = PostgresAuthRecordRepository()
    with repository_session:
        with pytest.raises(EntityNotFoundError):
            auth_record_repository.get_by_username("unknown", repository_session)