from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.models.auth import AuthRecord
from app.repositories.err import EntityNotFoundError
from app.repositories.postgres import PostgresSession
from app.repositories.session import RepositorySession


S = TypeVar("S", bound=RepositorySession)


class AuthRecordRepositoryInterface(ABC, Generic[S]):
    @abstractmethod
    def add(self, auth_record: AuthRecord, session: S):
        pass

    @abstractmethod
    def get_by_username(self, username: str, session: S) -> AuthRecord:
        """
        Raises:
            EntityNotFoundError: If no record is found with the provided username
        """
        pass


class PostgresAuthRecordRepository(AuthRecordRepositoryInterface):
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

    def add(self, auth_record: AuthRecord, session: PostgresSession):
        with session.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO auth_records (user_id, username, hashed_password) VALUES (%s, %s, %s);",
                (
                    auth_record.user_id,
                    auth_record.username,
                    auth_record.hashed_password,
                ),
            )
        session.commit()

    def get_by_username(self, username: str, session: PostgresSession) -> AuthRecord:
        with session.get_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, hashed_password FROM auth_records WHERE username = %s;",
                (username,),
            )
            result = cursor.fetchone()
            if result is None:
                raise EntityNotFoundError(f"No record found for username: {username}")
            return AuthRecord(
                user_id=result[0], username=result[1], hashed_password=result[2]
            )
