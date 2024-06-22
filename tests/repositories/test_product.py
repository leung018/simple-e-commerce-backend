from typing import Generator
import pytest

from app.models.product import Product
from app.repositories.product import (
    PostgresProductRepository,
    ProductRepositoryInterface,
)


@pytest.fixture
def product_repository() -> Generator[ProductRepositoryInterface, None, None]:
    yield PostgresProductRepository()


def new_product(id="p1", name="Hello", category="My category", price=6.7, quantity=5):
    return Product(id=id, name=name, category=category, price=price, quantity=quantity)


def test_should_save_and_get_product(product_repository: ProductRepositoryInterface):
    product = new_product()
    product_repository.save(product)
    assert product == product_repository.get_by_id(product_id=product.id)
