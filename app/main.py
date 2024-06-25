from fastapi import FastAPI
from app.routers.orders import router as order_router

app = FastAPI()

app.include_router(order_router, prefix="/orders", tags=["orders"])
