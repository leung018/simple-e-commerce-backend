from fastapi import FastAPI
from app.dependencies import get_repository_session
from app.repositories.migration import migrate_up
from app.routers.orders import router as order_router
from app.routers.auth import router as auth_router

app = FastAPI()

migrate_up(get_repository_session())

app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
