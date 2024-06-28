from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.dependencies import get_repository_session
from app.repositories.auth import auth_record_repository_factory
from app.repositories.base import RepositorySession
from app.repositories.user import user_repository_factory
from app.services.auth import AuthService, AuthServiceConfig


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def auth_service_factory(repository_session: RepositorySession) -> AuthService:
    return AuthService(
        AuthServiceConfig.from_env(),
        user_repository_factory,
        auth_record_repository_factory,
        repository_session,
    )


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    repository_session: Annotated[RepositorySession, Depends(get_repository_session)],
) -> str:
    auth_service = auth_service_factory(repository_session)
    user_id = auth_service.decode_user_id(token)
    return user_id
