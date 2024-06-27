import pytest
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.product import (
    PostgresProductRepository,
)
from tests.models.constructor import new_product


def test_should_save_and_get_product(repository_session: PostgresSession):
    product = new_product()
    product_repository = PostgresProductRepository(repository_session.new_operator)
    with repository_session:
        product_repository.save(product)
        assert product == product_repository.get_by_id(
            product.id,
        )


def test_should_raise_not_found_if_product_id_not_exist(
    repository_session: PostgresSession,
):
    product_repository = PostgresProductRepository(repository_session.new_operator)
    with repository_session:
        with pytest.raises(EntityNotFoundError) as exc_info:
            product_repository.get_by_id(
                "unknown",
            )
    assert str(exc_info.value) == str(
        EntityNotFoundError.create("product_id", "unknown")
    )


def test_should_save_able_to_update_product(repository_session: PostgresSession):
    product = new_product(name="old name", category="old category", price=9, quantity=1)
    product_repository = PostgresProductRepository(repository_session.new_operator)
    with repository_session:
        product_repository.save(product)

        product.name = "new name"
        product.category = "new category"
        product.price = 12
        product.quantity = 10
        product_repository.save(product)

        assert product_repository.get_by_id(product.id) == product
