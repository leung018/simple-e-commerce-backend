from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.models.order import Order, OrderItem, PurchaseInfo
from app.repositories.postgres import PostgresSession
from app.repositories.session import RepositorySession

S = TypeVar("S", bound=RepositorySession)


class OrderRepositoryInterface(ABC, Generic[S]):
    @abstractmethod
    def add(self, order: Order, session: S):
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: str, session: S) -> list[Order]:
        """
        Retrieves a list of orders, sorted such that the most recently created order appears first.

        Note: It might be possible to specify the preferred way of sorting using the Specification Pattern,
        but for the current project scope, the existing arrangement is sufficient.
        """
        pass


class PostgresOrderRepository(OrderRepositoryInterface):
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

    def add(self, order: Order, session: PostgresSession):
        with session.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders (id, user_id) VALUES (%s, %s)",
                (order.id, order.user_id),
            )
            for item in order.purchase_info.order_items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order.id, item.product_id, item.quantity),
                )

    def get_by_user_id(self, user_id: str, session: PostgresSession) -> list[Order]:
        orders = []
        with session.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, created_at FROM orders WHERE user_id = %s ORDER BY created_at DESC;",
                (user_id,),
            )
            order_rows = cursor.fetchall()
            for order_id, _ in order_rows:
                order_items = self._get_order_items(order_id, session)
                orders.append(
                    Order.create(id=order_id, user_id=user_id, order_items=order_items)
                )
            return orders

    def _get_order_items(
        self, order_id, session: PostgresSession
    ) -> tuple[OrderItem, ...]:
        with session.get_cursor() as cursor:
            cursor.execute(
                "SELECT product_id, quantity FROM order_items WHERE order_id = %s",
                (order_id,),
            )
            return tuple(
                OrderItem(product_id, quantity)
                for product_id, quantity in cursor.fetchall()
            )
