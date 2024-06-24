import pytest
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.product import (
    PostgresProductRepository,
)
from tests.models.constructor import new_product


def test_should_save_and_get_product(postgres_session: PostgresSession):
    product = new_product()
    product_repository = PostgresProductRepository()
    with postgres_session:
        product_repository.save(product, postgres_session)
        assert product == product_repository.get_by_id(product.id, postgres_session)


def test_should_raise_not_found_if_product_id_not_exist(
    postgres_session: PostgresSession,
):
    product_repository = PostgresProductRepository()
    with postgres_session:
        with pytest.raises(EntityNotFoundError):
            product_repository.get_by_id("unknown", postgres_session)


def test_should_save_able_to_update_product(postgres_session: PostgresSession):
    product = new_product(name="old name", category="old category", price=9, quantity=1)
    product_repository = PostgresProductRepository()
    with postgres_session:
        product_repository.save(product, postgres_session)

        product.name = "new name"
        product.category = "new category"
        product.price = 12
        product.quantity = 10
        product_repository.save(product, postgres_session)

        assert product_repository.get_by_id(product.id, postgres_session) == product
