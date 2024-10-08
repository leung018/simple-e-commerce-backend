from uuid import uuid4
from fastapi.testclient import TestClient
import pytest

from app.auth import auth_service_factory
from app.dependencies import (
    get_repository_session,
)
from app.main import app
from app.models.product import Product
from app.repositories.err import EntityNotFoundError
from app.repositories.order import order_repository_factory
from app.repositories.product import product_repository_factory
from app.repositories.base import RepositorySession
from app.services.auth import GetAccessTokenError, RegisterUserError
from app.services.order import PlaceOrderError
from tests.models.constructor import new_product

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_repository_session_dependency(repository_session):
    def my_get_repository_session():
        return repository_session

    app.dependency_overrides[get_repository_session] = my_get_repository_session


def test_should_login_respond_400_when_input_invalid():
    response = call_login_api(
        username="1", password="1234567"
    )  # username length not allow to be too short according to AuthInput rule. Expect the ValidationError raised from AuthInput can be handled
    assert response.status_code == 400


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
        "detail": RegisterUserError.format_username_exists_err_msg("user1")
    }


def test_should_reject_login_with_wrong_password():
    call_sign_up_api("myname", "mypassword")
    response = call_login_api("myname", "wrongpassword")
    assert response.json() == {
        "detail": GetAccessTokenError.USERNAME_OR_PASSWORD_ERR_MSG
    }


def test_should_place_order_and_get_placed_order(repository_session: RepositorySession):
    product = new_product(quantity=10, price=1)
    persist_product(product, repository_session)

    access_token = fetch_valid_access_token()

    order_id = str(uuid4())
    # Place order
    response = call_place_order_api(
        access_token, [{"product_id": product.id, "quantity": 5}], order_id=order_id
    )
    assert response.status_code == 201

    # Get orders
    response = call_get_orders_api(access_token)
    assert response.status_code == 200

    assert len(response.json()) == 1
    order_response = response.json()[0]
    assert order_response["id"] == order_id
    assert order_response["items"] == [{"id": product.id, "purchase_quantity": 5}]

    # check order id in response same as the one stored in repository
    user_id = auth_service_factory(repository_session).decode_user_id(access_token)
    with repository_session:
        order_repo = order_repository_factory(repository_session.new_operator)
        order_in_repo = order_repo.get_by_user_id(user_id)[0]
        assert order_response["id"] == order_in_repo.id


def test_should_response_400_if_my_value_error_throw_from_service_layer(
    repository_session: RepositorySession,
):
    product = new_product(quantity=5, price=1)
    persist_product(product, repository_session)

    access_token = fetch_valid_access_token()

    # Both PlaceOrderError and EntityNotFoundError are subclass of MyValueError. Expecting a generic error handling when MyValueError is raised from service layer

    # Place order with quantity more than available
    response = call_place_order_api(
        access_token, [{"product_id": product.id, "quantity": 10}]
    )
    assert response.status_code == 400
    assert response.json() == {"detail": PlaceOrderError.QUANTITY_NOT_ENOUGH_ERR_MSG}

    # Place order with non existing product
    response = call_place_order_api(
        access_token, [{"product_id": "unknown", "quantity": 1}]
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": EntityNotFoundError.format_err_msg("product_id", "unknown")
    }


def test_should_response_400_if_cannot_form_valid_purchase_info_from_request(
    repository_session: RepositorySession,
):
    product = new_product(quantity=5, price=1)
    persist_product(product, repository_session)

    access_token = fetch_valid_access_token()

    # PurchaseRequest that contains duplicate product_id can't form a valid PurchaseInfo. Expect error handling on this case
    response = call_place_order_api(
        access_token,
        [
            {"product_id": product.id, "quantity": 1},
            {"product_id": product.id, "quantity": 2},
        ],
    )
    assert response.status_code == 400


def persist_product(product: Product, repository_session: RepositorySession):
    product_repository = product_repository_factory(repository_session.new_operator)
    with repository_session:
        product_repository.save(product)
        repository_session.commit()


def fetch_valid_access_token():
    call_sign_up_api("myname", "mypassword")
    return call_login_api("myname", "mypassword").json()["access_token"]


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


def call_place_order_api(token: str, order_items: list, order_id: str = str(uuid4())):
    response = client.post(
        "/orders",
        json={"order_items": order_items, "order_id": order_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response


def call_get_orders_api(token: str):
    response = client.get(
        "/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response
