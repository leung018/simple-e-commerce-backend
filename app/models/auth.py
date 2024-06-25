from pydantic import Field
from pydantic.dataclasses import dataclass

USERNAME_MIN_LENGTH = 5
PASSWORD_MIN_LENGTH = 5


@dataclass(frozen=True)
class AuthInput:
    username: str = Field(
        min_length=USERNAME_MIN_LENGTH
    )  # TODO: May not allow whitespace for username and password
    password: str = Field(min_length=PASSWORD_MIN_LENGTH)


@dataclass(frozen=True)
class AuthRecord:
    username: str
    hashed_password: str
    user_id: str
