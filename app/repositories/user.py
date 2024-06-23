from abc import ABC, abstractmethod
from app.models.user import User
from app.repositories.postgres import new_postgres_conn, new_postgres_context_from_env


class UserRepositoryInterface(ABC):
    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> User:
        pass


class PostgresUserRepository(UserRepositoryInterface):
    def __init__(self):
        self._context = new_postgres_context_from_env()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR PRIMARY KEY,
                        balance NUMERIC
                    );  
                """
                )
                cur.execute(  # TODO: remove this later
                    """
                    DELETE FROM users;
                    """
                )
            conn.commit()

    def _conn(self):
        return new_postgres_conn(self._context)

    def save(self, user: User):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, balance)
                    VALUES (%s, %s)
                """,
                    (user.id, user.balance),
                )
            conn.commit()

    def get_by_id(self, user_id: str) -> User:
        with self._conn().cursor() as cur:
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
            raise NotImplementedError  # TODO: non happy path
