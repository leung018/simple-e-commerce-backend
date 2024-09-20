from abc import abstractmethod
from typing import Callable, TypeAlias, TypeVar

from psycopg import Cursor
import psycopg

from app.models.order import Order, OrderItem
from app.repositories.base import AbstractRepository
from app.repositories.err import EntityAlreadyExistsError

Operator = TypeVar("Operator")


class OrderRepository(AbstractRepository[Operator]):
    @abstractmethod
    def add(self, order: Order):
        """
        Raises:
            EntityAlreadyExistsError: If order already exists
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> list[Order]:
        """
        Retrieves a list of orders, sorted such that the most recently created order appears first.

        Note: It might be possible to specify the preferred way of sorting using the Specification Pattern,
        but for the current project scope, the existing arrangement is sufficient.
        """
        pass


OrderRepositoryFactory: TypeAlias = Callable[
    [Callable[[], Operator]], OrderRepository[Operator]
]


def order_repository_factory(new_operator):
    return PostgresOrderRepository(new_operator)


class PostgresOrderRepository(OrderRepository[Cursor]):
    CREATE_TABLES_IF_NOT_EXISTS = """
        CREATE TABLE IF NOT EXISTS orders (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items (
            order_id VARCHAR(36) NOT NULL,
            product_id VARCHAR(36) NOT NULL,
            quantity INT NOT NULL,
            PRIMARY KEY (order_id, product_id)
        );
    """
    DROP_TABLES = """
        DROP TABLE order_items, orders;
    """

    def add(self, order: Order):
        with self.new_operator() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO orders (id, user_id) VALUES (%s, %s)",
                    (order.id, order.user_id),
                )
            except psycopg.errors.UniqueViolation:
                raise EntityAlreadyExistsError.create("id", order.id)

            for item in order.order_items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order.id, item.product_id, item.quantity),
                )

    def get_by_user_id(self, user_id: str) -> list[Order]:
        orders = []
        with self.new_operator() as cursor:
            cursor.execute(
                "SELECT id, created_at FROM orders WHERE user_id = %s ORDER BY created_at DESC;",
                (user_id,),
            )
            order_rows = cursor.fetchall()
            for order_id, _ in order_rows:
                order_items = self._get_order_items(order_id)
                orders.append(
                    Order(id=order_id, user_id=user_id, order_items=order_items)
                )
            return orders

    def _get_order_items(self, order_id) -> tuple[OrderItem, ...]:
        with self.new_operator() as cursor:
            cursor.execute(
                "SELECT product_id, quantity FROM order_items WHERE order_id = %s",
                (order_id,),
            )
            return tuple(
                OrderItem(product_id, quantity)
                for product_id, quantity in cursor.fetchall()
            )
