from abc import ABC, abstractmethod

from app.models.product import Product
from app.postgres import new_postgres_conn, new_postgres_context_from_env


class ProductRepositoryInterface(ABC):
    @abstractmethod
    def save(self, product: Product):
        pass

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product:
        pass


class PostgresProductRepository(ProductRepositoryInterface):
    def __init__(self):
        self.conn = new_postgres_conn(new_postgres_context_from_env())
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    category VARCHAR NOT NULL,
                    price NUMERIC,
                    quantity INTEGER
                );  
            """
            )

    def save(self, product: Product):
        with self.conn.cursor() as cur:
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

    def get_by_id(self, product_id: str) -> Product:
        with self.conn.cursor() as cur:
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
