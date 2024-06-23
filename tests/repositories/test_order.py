from typing import Optional
from app.models.order import Order
from app.repositories.order import PostgresOrderRepository
from app.repositories.postgres import PostgresSession


def new_order(id="o1", user_id="u1", product_ids: tuple[str, ...] = ("p1", "p2")):
    Order(id="o1", user_id="u1", product_ids=product_ids)
    return Order(id, user_id, product_ids)


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
