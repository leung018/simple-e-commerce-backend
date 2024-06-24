from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres import PostgresSession
from tests.models.constructor import new_order


def test_should_save_and_get_by_user_id(postgres_session: PostgresSession):
    order = new_order(user_id="u1")
    order_repository = PostgresOrderRepository()
    with postgres_session:
        order_repository.add(order, postgres_session)

        retrieved_orders = order_repository.get_by_user_id("u1", postgres_session)
        assert len(retrieved_orders) == 1
        assert retrieved_orders[0] == order

        assert len(order_repository.get_by_user_id("u2", postgres_session)) == 0


def test_should_get_by_user_id_return_the_orders_with_more_recently_created_at_first(
    postgres_session: PostgresSession,
):
    order1 = new_order(id="p0", user_id="u1")
    order2 = new_order(id="p1", user_id="u1")

    order_repository = PostgresOrderRepository()
    with postgres_session:
        # explicitly commit here, so that the creation time will be have difference
        order_repository.add(order1, postgres_session)
        postgres_session.commit()

        order_repository.add(order2, postgres_session)
        postgres_session.commit()

        retrieved_orders = order_repository.get_by_user_id("u1", postgres_session)
        assert retrieved_orders == [order2, order1]
