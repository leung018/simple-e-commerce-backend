from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user_id
from app.dependencies import get_repository_session
from app.err import MyValueError
from app.models.order import Order, PurchaseInfo
from app.repositories.order import order_repository_factory
from app.repositories.product import product_repository_factory
from app.repositories.base import RepositorySession
from app.repositories.user import user_repository_factory
from app.services.order import OrderService


router = APIRouter()


class OrderItemModel(BaseModel):
    id: str
    purchase_quantity: int


class OrderModel(BaseModel):
    id: str
    items: list[OrderItemModel]

    @staticmethod
    def from_domain(order: Order):
        return OrderModel(
            id=order.id,
            items=[
                OrderItemModel(id=item.product_id, purchase_quantity=item.quantity)
                for item in order.purchase_info.order_items
            ],
        )


@router.post("/", status_code=201)
def place_order(
    purchase_info: PurchaseInfo,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    repository_session: Annotated[RepositorySession, Depends(get_repository_session)],
):
    order_service = OrderService(
        user_repository_factory,
        product_repository_factory,
        order_repository_factory,
        repository_session,
    )

    try:
        order_service.place_order(current_user_id, purchase_info)
    except MyValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[OrderModel])
def get_orders(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    repository_session: Annotated[RepositorySession, Depends(get_repository_session)],
):
    order_repository = order_repository_factory(repository_session.new_operator)
    with repository_session:
        orders = order_repository.get_by_user_id(current_user_id)
    return list(map(OrderModel.from_domain, orders))
