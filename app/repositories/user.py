from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from psycopg import Cursor
from app.models.user import User
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.session import AbstractRepository, RepositorySession


Operator = TypeVar("Operator")


class UserRepositoryInterface(AbstractRepository[Operator]):
    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> User:
        """
        Raises:
            EntityNotFoundError: If no user is found with the provided id.
        """
        pass


class PostgresUserRepository(UserRepositoryInterface[Cursor]):
    CREATE_TABLE_IF_NOT_EXISTS = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            balance NUMERIC
        );
    """

    DROP_TABLE = """
        DROP TABLE users;
    """

    def save(self, user: User):
        with self.get_operator() as cur:
            cur.execute(
                """
                INSERT INTO users (id, balance)
                VALUES (%s, %s)
                ON CONFLICT (id)
                DO UPDATE SET balance = EXCLUDED.balance;
            """,
                (user.id, user.balance),
            )

    def get_by_id(self, user_id: str) -> User:
        with self.get_operator() as cur:
            cur.execute(
                "SELECT id, balance FROM users WHERE id = %s;",
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return User(
                    id=row[0],
                    balance=row[1],
                )
            raise EntityNotFoundError("user_id: {} doesn't exist".format(user_id))
