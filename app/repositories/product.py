from abc import ABC, abstractmethod
from typing import Generic, TypeVar, SupportsAbs

from app.models.product import Product
from app.repositories.postgres import (
    PostgresSession,
)
from app.repositories.session import RepositorySession

S = TypeVar("S", bound=SupportsAbs[RepositorySession])


class ProductRepositoryInterface(ABC, Generic[S]):
    @abstractmethod
    def save(self, product: Product, session: S):
        pass

    @abstractmethod
    def get_by_id(self, product_id: str, session: S) -> Product:
        pass


class PostgresProductRepository(ProductRepositoryInterface):
    def save(self, product: Product, session: PostgresSession):
        with session.conn.cursor() as cur:
            cur.execute(
                """
                    INSERT INTO products (id, name, category, price, quantity)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    product.id,
                    product.name,
                    product.category,
                    product.price,
                    product.quantity,
                ),
            )

    def get_by_id(self, product_id: str, session: PostgresSession) -> Product:
        with session.conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, category, price, quantity FROM products WHERE id = %s;",
                (product_id,),
            )
            row = cur.fetchone()
            if row:
                return Product(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    price=row[3],
                    quantity=row[4],
                )
            raise NotImplementedError  # TODO: non happy path
