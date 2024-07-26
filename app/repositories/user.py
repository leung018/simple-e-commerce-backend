from abc import abstractmethod
from typing import Callable, TypeAlias, TypeVar

from psycopg import Cursor
from app.models.user import User
from app.repositories.err import EntityNotFoundError
from app.repositories.base import AbstractRepository
from app.repositories.postgres.helper import select_query_helper


Operator = TypeVar("Operator")


class UserRepository(AbstractRepository[Operator]):
    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def get_by_id(
        self,
        user_id: str,
        exclusive_lock: bool = False,
    ) -> User:
        """
        Raises:
            EntityNotFoundError: If no user is found with the provided id.
        """
        pass


UserRepositoryFactory: TypeAlias = Callable[
    [Callable[[], Operator]], UserRepository[Operator]
]


def user_repository_factory(new_operator):
    return PostgresUserRepository(new_operator)


class PostgresUserRepository(UserRepository[Cursor]):
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
        with self.new_operator() as cur:
            cur.execute(
                """
                INSERT INTO users (id, balance)
                VALUES (%s, %s)
                ON CONFLICT (id)
                DO UPDATE SET balance = EXCLUDED.balance;
            """,
                (user.id, user.balance),
            )

    def get_by_id(self, user_id: str, exclusive_lock: bool = False) -> User:
        with self.new_operator() as cur:
            query = select_query_helper(
                "SELECT id, balance FROM users WHERE id = %s", for_update=exclusive_lock
            )
            cur.execute(
                query,
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return User(
                    id=row[0],
                    balance=row[1],
                )
            raise EntityNotFoundError.create("user_id", user_id)
