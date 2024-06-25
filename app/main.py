from fastapi import FastAPI
from app.dependencies import get_repository_session
from app.repositories.migration import setup_tables
from app.routers.orders import router as order_router

app = FastAPI()

setup_tables(get_repository_session())

app.include_router(order_router, prefix="/orders", tags=["orders"])
