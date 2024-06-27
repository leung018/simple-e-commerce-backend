from fastapi.testclient import TestClient
import pytest

from app.auth import auth_service_factory
from app.dependencies import (
    get_repository_session,
)
from app.main import app
from app.models.product import Product
from app.repositories.order import order_repository_factory
from app.repositories.product import product_repository_factory
from app.repositories.base import RepositorySession
from app.services.auth import GetAccessTokenError, RegisterUserError
from tests.models.constructor import new_product

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_repository_session_dependency(repository_session):
    def my_get_repository_session():
        return repository_session

    app.dependency_overrides[get_repository_session] = my_get_repository_session


def test_should_sign_up_and_login_respond_properly():
    response = call_sign_up_api("myname", "mypassword")
    assert response.status_code == 201

    response = call_login_api("myname", "mypassword")
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_should_reject_sign_up_with_same_user():
    call_sign_up_api("user1", "mypassword")

    response = call_sign_up_api("user1", "mypassword2")
    assert response.status_code == 400
    assert response.json() == {
        "detail": RegisterUserError.format_username_exists_error("user1")
    }


def test_should_reject_login_with_wrong_password():
    call_sign_up_api("myname", "mypassword")
    response = call_login_api("myname", "wrongpassword")
    assert response.json() == {"detail": GetAccessTokenError.USERNAME_OR_PASSWORD_ERROR}


def test_should_place_order_and_get_placed_order(repository_session: RepositorySession):
    # Initialize product
    product = new_product(quantity=10, price=1)
    persist_product(product, repository_session)

    # Initialize user
    call_sign_up_api("myname", "mypassword")
    access_token = call_login_api("myname", "mypassword").json()["access_token"]

    response = call_place_order_api(
        access_token, [{"product_id": product.id, "quantity": 5}]
    )
    assert response.status_code == 201

    # get orders api
    response = call_get_orders_api(access_token)
    assert response.status_code == 200

    assert len(response.json()) == 1
    order_response = response.json()[0]
    assert order_response["items"] == [{"id": product.id, "purchase_quantity": 5}]

    # check order id in response same as the one stored in repository
    user_id = auth_service_factory(repository_session).decode_user_id(access_token)
    with repository_session:
        order_repo = order_repository_factory(repository_session.new_operator)
        order_in_repo = order_repo.get_by_user_id(user_id)[0]
        assert order_response["id"] == order_in_repo.id


def persist_product(product: Product, repository_session: RepositorySession):
    product_repository = product_repository_factory(repository_session.new_operator)
    with repository_session:
        product_repository.save(product)
        repository_session.commit()


def call_login_api(username: str, password: str):
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    return response


def call_sign_up_api(username: str, password: str):
    response = client.post(
        "/auth/signup", json={"username": username, "password": password}
    )
    return response


def call_place_order_api(token: str, order_items: list):
    response = client.post(
        "/orders",
        json={"order_items": order_items},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response


def call_get_orders_api(token: str):
    response = client.get(
        "/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response
