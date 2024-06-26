from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.dependencies import get_repository_session
from app.models.auth import AuthInput
from app.repositories.auth import auth_record_repository_factory
from app.repositories.base import RepositorySession
from app.repositories.user import user_repository_factory
from app.services.auth import AuthService, AuthServiceConfig, RegisterUserError


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup", status_code=201)
def sign_up(
    auth_input: AuthInput,
    repository_session: RepositorySession = Depends(get_repository_session),
):
    user_repository = user_repository_factory(repository_session.new_operator)
    auth_record_repository = auth_record_repository_factory(
        repository_session.new_operator
    )
    auth_service = AuthService(
        AuthServiceConfig.from_env(),
        user_repository,
        auth_record_repository,
        repository_session,
    )

    try:
        auth_service.sign_up(auth_input)
    except RegisterUserError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return Token(access_token="todo", token_type="bearer")
