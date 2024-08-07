from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ValidationError

from app.auth import auth_service_factory
from app.dependencies import get_repository_session
from app.models.auth import AuthInput
from app.repositories.base import RepositorySession
from app.services.auth import (
    GetAccessTokenError,
    RegisterUserError,
)


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup", status_code=201)
def sign_up(
    auth_input: AuthInput,  # Reuse domain model in the API layer because it can has the validation logic of the domain model and response bad request if the input is invalid.
    # If future wanna refactor the domain model without affecting the API layer, consider using a separate model for the API layer.
    repository_session: Annotated[RepositorySession, Depends(get_repository_session)],
):
    auth_service = auth_service_factory(repository_session)

    try:
        auth_service.sign_up(auth_input)
    except RegisterUserError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository_session: Annotated[RepositorySession, Depends(get_repository_session)],
):
    try:
        auth_input = AuthInput(username=form_data.username, password=form_data.password)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    auth_service = auth_service_factory(repository_session)

    try:
        access_token = auth_service.get_access_token(auth_input)
    except GetAccessTokenError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Token(access_token=access_token, token_type="bearer")
