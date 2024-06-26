from abc import abstractmethod
from typing import TypeVar

from psycopg import Cursor

from app.models.product import Product
from app.repositories.err import EntityNotFoundError
from app.repositories.base import AbstractRepository

Operator = TypeVar("Operator")


class ProductRepository(AbstractRepository[Operator]):
    @abstractmethod
    def save(self, product: Product):
        pass

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product:
        """
        Raises:
            EntityNotFoundError: If no product is found with the provided id.
        """
        pass


def product_repository_factory(new_operator):
    return PostgresProductRepository(new_operator)


class PostgresProductRepository(ProductRepository[Cursor]):
    CREATE_TABLE_IF_NOT_EXISTS = """
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            price NUMERIC,
            quantity INTEGER
        );  
    """
    DROP_TABLE = """
        DROP TABLE products;
    """

    def save(self, product: Product):
        with self.new_operator() as cur:
            cur.execute(
                """
                    INSERT INTO products (id, name, category, price, quantity)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        category = EXCLUDED.category,
                        price = EXCLUDED.price,
                        quantity = EXCLUDED.quantity;
                """,
                (
                    product.id,
                    product.name,
                    product.category,
                    product.price,
                    product.quantity,
                ),
            )

    def get_by_id(self, product_id: str) -> Product:
        with self.new_operator() as cur:
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
            raise EntityNotFoundError("product_id: {} doesn't exist".format(product_id))
