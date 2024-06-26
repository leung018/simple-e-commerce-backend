from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from typing import Generic, Optional, TypeVar
from uuid import uuid4
import jwt
from passlib.context import CryptContext

from app.err import MyValueError
from app.models.auth import AuthInput, AuthRecord
from app.models.user import USER_INITIAL_BALANCE, User
from app.repositories.auth import AuthRecordRepositoryInterface
from app.repositories.err import EntityNotFoundError
from app.repositories.base import RepositorySession
from app.repositories.user import UserRepositoryInterface

Operator = TypeVar("Operator")


class RegisterUserError(MyValueError):
    pass


class GetAccessTokenError(MyValueError):
    pass


class DecodeAccessTokenError(MyValueError):
    pass


@dataclass(frozen=True)
class AuthServiceConfig:
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_days: int = 7

    @staticmethod
    def from_env():
        jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY",
            "700ff87314881a7ea2fa0f7b451280006dbc657ecc2537925dbb947613f5dd22",
        )
        jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        access_token_expire_days = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", 7))

        return AuthServiceConfig(
            jwt_secret_key=jwt_secret_key,
            jwt_algorithm=jwt_algorithm,
            access_token_expire_days=access_token_expire_days,
        )


class AuthService(Generic[Operator]):
    def __init__(
        self,
        auth_service_config: AuthServiceConfig,
        user_repository: UserRepositoryInterface[Operator],
        auth_repository: AuthRecordRepositoryInterface[Operator],
        repository_session: RepositorySession[Operator],
    ):
        self._auth_service_config = auth_service_config
        self._user_repository = user_repository
        self._auth_repository = auth_repository
        self._session = repository_session

    def register_user(self, auth_input: AuthInput):
        with self._session:
            if self._get_auth_record(auth_input.username):
                raise RegisterUserError(
                    "username: {} already exists".format(auth_input.username)
                )

            user = self._new_user()
            self._user_repository.save(user)
            self._auth_repository.add(self._new_auth_record(user.id, auth_input))
            self._session.commit()

    def _new_user(self):
        user = User(id=str(uuid4()), balance=USER_INITIAL_BALANCE)
        return user

    def _new_auth_record(self, new_user_id: str, auth_input: AuthInput):
        return AuthRecord(
            user_id=new_user_id,
            hashed_password=get_password_hash(auth_input.password),
            username=auth_input.username,
        )

    def _get_auth_record(self, username: str) -> Optional[AuthRecord]:
        try:
            return self._auth_repository.get_by_username(username)
        except EntityNotFoundError:
            return None

    def get_access_token(self, auth_input: AuthInput) -> str:
        with self._session:
            auth_record = self._get_auth_record(auth_input.username)

            if not auth_record or not is_password_valid(
                auth_input.password, auth_record.hashed_password
            ):
                raise GetAccessTokenError("username or password is not correct")

            user = self._user_repository.get_by_id(auth_record.user_id)

        return self._create_access_token(user.id)

    def _create_access_token(self, user_id: str):
        to_encode: dict = {"sub": user_id}
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._auth_service_config.access_token_expire_days
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self._auth_service_config.jwt_secret_key,
            algorithm=self._auth_service_config.jwt_algorithm,
        )
        return encoded_jwt

    def decode_user_id(self, access_token: str) -> str:
        try:
            payload = jwt.decode(
                access_token,
                self._auth_service_config.jwt_secret_key,
                algorithms=[self._auth_service_config.jwt_algorithm],
            )
        except jwt.InvalidTokenError:
            raise DecodeAccessTokenError
        user_id = payload.get("sub")
        return user_id


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_password_valid(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
