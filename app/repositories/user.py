from abc import ABC, abstractmethod
from typing import Generic, SupportsAbs, TypeVar
from app.models.user import User
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.session import RepositorySession


S = TypeVar("S", bound=SupportsAbs[RepositorySession])


class UserRepositoryInterface(ABC, Generic[S]):
    @abstractmethod
    def save(self, user: User, session: S):
        pass

    @abstractmethod
    def get_by_id(self, user_id: str, session: S) -> User:
        pass


class PostgresUserRepository(UserRepositoryInterface):
    CREATE_TABLE_IF_NOT_EXISTS = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            balance NUMERIC
        );
    """

    DROP_TABLE = """
        DROP TABLE users;
    """

    def save(self, user: User, session: PostgresSession):
        with session.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (id, balance)
                VALUES (%s, %s)
            """,
                (user.id, user.balance),
            )

    def get_by_id(self, user_id: str, session: PostgresSession) -> User:
        with session.conn.cursor() as cur:
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
