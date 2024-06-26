from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.models.auth import AuthInput


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup", status_code=201)
def sign_up(auth_input: AuthInput):
    pass


@router.post("/login")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return Token(access_token="todo", token_type="bearer")
