import pytest
from app.repositories.postgres import PostgresSession
from app.repositories.order import PostgresOrderRepository
from tests.models.constructor import new_order


def test_should_session_not_commit_work_by_default(repository_session: PostgresSession):
    order = new_order(user_id="u1")
    with repository_session:
        order_repository = PostgresOrderRepository(repository_session.get_operator)
        order_repository.add(order)
        assert len(order_repository.get_by_user_id("u1")) == 1

    with repository_session:
        assert len(order_repository.get_by_user_id("u1")) == 0


def test_should_committed_changes_persist_to_other_session_block(
    repository_session: PostgresSession,
):
    order = new_order(user_id="u1")
    with repository_session:
        order_repository = PostgresOrderRepository(repository_session.get_operator)
        order_repository.add(order)
        repository_session.commit()

    with repository_session:
        assert len(order_repository.get_by_user_id("u1")) == 1


def test_should_able_to_rollback_change_in_the_same_session_block(
    repository_session: PostgresSession,
):
    order = new_order(user_id="u1")
    with repository_session:
        order_repository = PostgresOrderRepository(repository_session.get_operator)
        order_repository.add(order)
        assert len(order_repository.get_by_user_id("u1")) == 1

        repository_session.rollback()

        assert len(order_repository.get_by_user_id("u1")) == 0


def test_should_not_rollback_committed_changes(
    repository_session: PostgresSession,
):
    order1 = new_order(user_id="u1", id="o1")
    order2 = new_order(user_id="u1", id="o2")

    with repository_session:
        order_repository = PostgresOrderRepository(repository_session.get_operator)
        order_repository.add(order1)
        repository_session.commit()

        order_repository.add(order2)
        assert len(order_repository.get_by_user_id("u1")) == 2

        repository_session.rollback()
        assert len(order_repository.get_by_user_id("u1")) == 1

    with repository_session:
        assert len(order_repository.get_by_user_id("u1")) == 1


def test_should_rollback_on_error(repository_session: PostgresSession):
    class MyException(Exception):
        pass

    order = new_order(user_id="u1")
    with pytest.raises(MyException):
        with repository_session:
            order_repository = PostgresOrderRepository(repository_session.get_operator)
            order_repository.add(order)
            raise MyException()

    with repository_session:
        order_repository = PostgresOrderRepository(repository_session.get_operator)
        assert len(order_repository.get_by_user_id("u1")) == 0
