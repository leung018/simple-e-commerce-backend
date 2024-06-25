from typing import Union
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class AuthInput:
    username: str
    password: str


@dataclass(frozen=True)
class AuthRecord:
    username: str
    hashed_password: str
    user_id: str
