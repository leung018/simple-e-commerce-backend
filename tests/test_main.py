from fastapi.testclient import TestClient

from app.dependencies import (
    get_product_repository,
    get_repository_session,
    get_user_repository,
)
from app.main import app
from app.repositories.session import RepositorySession
from app.routers.orders import DUMMY_USER_ID
from tests.models.constructor import new_product, new_user

client = TestClient(app)


def test_should_create_and_get_order(repository_session: RepositorySession):
    user_repository = get_user_repository()
    product_repository = get_product_repository()

    product = new_product(quantity=10, price=1)

    with repository_session:
        user_repository.save(
            new_user(id=DUMMY_USER_ID, balance=100), repository_session
        )
        product_repository.save(product, repository_session)
        repository_session.commit()

    response = client.post(
        "/orders", json={"order_items": [{"product_id": product.id, "quantity": 5}]}
    )
    assert response.status_code == 201

    # TODO
