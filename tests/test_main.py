from fastapi.testclient import TestClient
import pytest

from app.dependencies import (
    get_repository_session,
)
from app.main import app
from app.models.product import Product
from app.models.user import User
from app.repositories.order import order_repository_factory
from app.repositories.product import product_repository_factory
from app.repositories.base import RepositorySession
from app.repositories.user import user_repository_factory
from app.routers.orders import DUMMY_USER_ID
from tests.models.constructor import new_product, new_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_repository_session_dependency(repository_session):
    def my_get_repository_session():
        return repository_session

    app.dependency_overrides[get_repository_session] = my_get_repository_session


def test_should_place_order_and_get_placed_order(repository_session: RepositorySession):
    product = new_product(quantity=10, price=1)
    create_product(product, repository_session)

    create_user(new_user(id=DUMMY_USER_ID, balance=100), repository_session)

    # place order api
    response = client.post(
        "/orders", json={"order_items": [{"product_id": product.id, "quantity": 5}]}
    )
    assert response.status_code == 201

    # get orders api
    response = client.get("/orders")
    assert response.status_code == 200

    assert len(response.json()) == 1
    order_response = response.json()[0]
    assert order_response["items"] == [{"id": product.id, "purchase_quantity": 5}]

    # check order id in response same as the one stored in repository
    with repository_session:
        order_repo = order_repository_factory(repository_session.get_operator)
        order_in_repo = order_repo.get_by_user_id(DUMMY_USER_ID)[0]
        assert order_response["id"] == order_in_repo.id


def create_product(product: Product, repository_session: RepositorySession):
    product_repository = product_repository_factory(repository_session.get_operator)
    with repository_session:
        product_repository.save(product)
        repository_session.commit()


def create_user(user: User, repository_session: RepositorySession):
    user_repository = user_repository_factory(repository_session.get_operator)
    with repository_session:
        user_repository.save(user)
        repository_session.commit()
