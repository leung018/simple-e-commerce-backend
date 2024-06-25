from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import (
    get_order_repository,
    get_product_repository,
    get_repository_session,
    get_user_repository,
)
from app.models.order import Order, PurchaseInfo
from app.repositories.order import OrderRepositoryInterface
from app.repositories.session import RepositorySession
from app.services.order import OrderService

DUMMY_USER_ID = "dummy_user_id"  # TODO: For testing in current stage, remove it after oauth is added


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
    user_repository=Depends(get_user_repository),
    product_repository=Depends(get_product_repository),
    order_repository=Depends(get_order_repository),
    repository_session=Depends(get_repository_session),
):
    order_service = OrderService(
        user_repository, product_repository, order_repository, repository_session
    )
    order_service.place_order(DUMMY_USER_ID, purchase_info)


@router.get("/", response_model=list[OrderModel])
def get_orders(
    order_repository: OrderRepositoryInterface = Depends(get_order_repository),
    repository_session: RepositorySession = Depends(get_repository_session),
):
    with repository_session:
        orders = order_repository.get_by_user_id(DUMMY_USER_ID, repository_session)
    return list(map(OrderModel.from_domain, orders))
