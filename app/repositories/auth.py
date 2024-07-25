from abc import abstractmethod
from typing import Callable, TypeAlias, TypeVar

from psycopg import Cursor
import psycopg

from app.models.auth import AuthRecord
from app.repositories.err import EntityAlreadyExistsError, EntityNotFoundError
from app.repositories.base import AbstractRepository


Operator = TypeVar("Operator")


class AuthRecordRepository(AbstractRepository[Operator]):
    @abstractmethod
    def add(self, auth_record: AuthRecord):
        """
        Raises:
            EntityAlreadyExistsError: If a record with the provided username already exists
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> AuthRecord:
        """
        Raises:
            EntityNotFoundError: If no record is found with the provided username
        """
        pass


AuthRecordRepositoryFactory: TypeAlias = Callable[
    [Callable[[], Operator]], AuthRecordRepository[Operator]
]


def auth_record_repository_factory(new_operator):
    return PostgresAuthRecordRepository(new_operator)


class PostgresAuthRecordRepository(AuthRecordRepository[Cursor]):
    CREATE_TABLE_IF_NOT_EXISTS = """
        CREATE TABLE IF NOT EXISTS auth_records (
            user_id VARCHAR PRIMARY KEY,
            username VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL
        );
    """

    DROP_TABLE = """
        DROP TABLE auth_records;
    """

    def add(self, auth_record: AuthRecord):
        with self.new_operator() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO auth_records (user_id, username, hashed_password) VALUES (%s, %s, %s);",
                    (
                        auth_record.user_id,
                        auth_record.username,
                        auth_record.hashed_password,
                    ),
                )
            except psycopg.errors.UniqueViolation:
                raise EntityAlreadyExistsError.create("username", auth_record.username)

    def get_by_username(self, username: str) -> AuthRecord:
        with self.new_operator() as cursor:
            cursor.execute(
                "SELECT user_id, username, hashed_password FROM auth_records WHERE username = %s;",
                (username,),
            )
            result = cursor.fetchone()
            if result is None:
                raise EntityNotFoundError.create("username", username)
            return AuthRecord(
                user_id=result[0], username=result[1], hashed_password=result[2]
            )
