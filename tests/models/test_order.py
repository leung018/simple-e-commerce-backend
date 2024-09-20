from uuid import uuid4
from pydantic import ValidationError
import pytest
from app.models.order import OrderItem, PurchaseInfo


def new_purchase_info(
    order_items=(OrderItem("p1", 3), OrderItem("p2", 4)), order_id="o1"
):
    return PurchaseInfo(order_items, order_id)


def test_should_purchase_info_not_accept_empty_order_items():
    with pytest.raises(ValidationError) as exc_info:
        new_purchase_info(order_items=())
    assert "order_items must not be empty" in str(exc_info.value)


def test_should_purchase_info_not_accept_duplicate_product_id():
    with pytest.raises(ValidationError) as exc_info:
        new_purchase_info(order_items=(OrderItem("p1", 3), OrderItem("p1", 4)))
    assert "order_items must not contain duplicate product_id" in str(exc_info.value)

    # won't raise error
    new_purchase_info(order_items=(OrderItem("p1", 3), OrderItem("p2", 4)))
