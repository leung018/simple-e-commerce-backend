import pytest
from app.repositories.postgres import PostgresSession, new_postgres_config_from_env
from app.repositories.order import PostgresOrderRepository
from tests.models.constructor import new_order


def test_should_session_not_commit_work_by_default(postgres_session: PostgresSession):
    order = new_order(user_id="u1")
    with postgres_session:
        order_repository = PostgresOrderRepository()
        order_repository.add(order, postgres_session)
        assert len(order_repository.get_by_user_id("u1", postgres_session)) == 1

    with postgres_session:
        assert len(order_repository.get_by_user_id("u1", postgres_session)) == 0


def test_should_session_committed_changes_persist_to_other_session(
    postgres_session: PostgresSession,
):
    order = new_order(user_id="u1")
    with postgres_session:
        order_repository = PostgresOrderRepository()
        order_repository.add(order, postgres_session)
        postgres_session.commit()

    with postgres_session:
        assert len(order_repository.get_by_user_id("u1", postgres_session)) == 1


def test_should_rollback_on_error(postgres_session: PostgresSession):
    class MyException(Exception):
        pass

    order = new_order(user_id="u1")
    with pytest.raises(MyException):
        with postgres_session:
            order_repository = PostgresOrderRepository()
            order_repository.add(order, postgres_session)
            raise MyException()

    with postgres_session:
        order_repository = PostgresOrderRepository()
        assert len(order_repository.get_by_user_id("u1", postgres_session)) == 0
