import pytest
from app.repositories.err import EntityAlreadyExistsError
from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres.session import PostgresSession
from tests.models.constructor import new_order


def test_should_save_and_get_by_user_id(repository_session: PostgresSession):
    order = new_order(user_id="u1")
    order_repository = PostgresOrderRepository(repository_session.new_operator)
    with repository_session:
        order_repository.add(order)

        retrieved_orders = order_repository.get_by_user_id("u1")
        assert len(retrieved_orders) == 1
        assert retrieved_orders[0] == order

        assert len(order_repository.get_by_user_id("u2")) == 0


def test_should_get_by_user_id_return_the_orders_with_more_recently_created_at_first(
    repository_session: PostgresSession,
):
    order1 = new_order(id="p0", user_id="u1")
    order2 = new_order(id="p1", user_id="u1")

    order_repository = PostgresOrderRepository(repository_session.new_operator)
    with repository_session:
        # explicitly commit here after each time of adding order, so there will be difference in the creation time in the record
        order_repository.add(order1)
        repository_session.commit()

        order_repository.add(order2)
        repository_session.commit()

        retrieved_orders = order_repository.get_by_user_id("u1")
        assert retrieved_orders == [order2, order1]


def test_should_raise_entity_already_exists_if_order_already_exists(
    repository_session: PostgresSession,
):
    order_repository = PostgresOrderRepository(repository_session.new_operator)

    order = new_order()
    with repository_session:
        order_repository.add(order)
        with pytest.raises(EntityAlreadyExistsError) as exc_info:
            order_repository.add(order)
    assert str(exc_info.value) == EntityAlreadyExistsError.format_err_msg(
        "id", order.id
    )
