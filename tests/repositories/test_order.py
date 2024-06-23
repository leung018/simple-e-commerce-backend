from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres import PostgresSession
from tests.repositories.constructor import new_order


def test_should_save_and_get_by_user_id(postgres_session: PostgresSession):
    order = new_order(user_id="u1")
    order_repository = PostgresOrderRepository()
    with postgres_session:
        order_repository.add(order, postgres_session)
        postgres_session.commit()

    retrieved_orders = order_repository.get_by_user_id("u1", postgres_session)
    assert len(retrieved_orders) == 1
    assert retrieved_orders[0] == order

    assert len(order_repository.get_by_user_id("u2", postgres_session)) == 0
