from fastapi import APIRouter
from pydantic import BaseModel

DUMMY_USER_ID = "dummy_user_id"  # TODO: For testing in current stage, remove it after oauth is added


router = APIRouter()


class PlaceOrderRequest(BaseModel):
    product_id_to_quantity: dict[str, int]


class ProductModel(BaseModel):
    id: str
    name: str
    category: str


class OrderModel(BaseModel):
    id: str
    products: list[ProductModel]


@router.post("/", status_code=201)
def place_order(place_order_request: PlaceOrderRequest):
    pass


@router.get("/", response_model=list[OrderModel])
def get_orders():
    pass
