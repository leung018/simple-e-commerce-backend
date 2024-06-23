from app.models.product import Product
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
        postgres_session.commit()
    assert product == product_repository.get_by_id(product.id, postgres_session)