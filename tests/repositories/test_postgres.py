from app.repositories.postgres import PostgresSession, new_postgres_context_from_env
from app.repositories.order import PostgresOrderRepository
from tests.repositories.test_order import new_order


def new_session():
    return PostgresSession(new_postgres_context_from_env())


def test_should_session_not_commit_work_by_default(postgres_session: PostgresSession):
    order = new_order(user_id="u1")
    with postgres_session:
        order_repository = PostgresOrderRepository()
        order_repository.add(order, postgres_session)

    other_session = new_session()

    with other_session:
        assert len(order_repository.get_by_user_id("u1", other_session)) == 0
