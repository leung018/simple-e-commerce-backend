import pytest
from app.models.product import Product
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.product import (
    PostgresProductRepository,
)


def new_product(id="p1", name="Hello", category="My category", price=6.7, quantity=5):
    return Product(id=id, name=name, category=category, price=price, quantity=quantity)


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
