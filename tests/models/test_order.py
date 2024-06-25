from pydantic import ValidationError
import pytest
from app.models.order import OrderItem, PurchaseInfo


def test_should_purchase_info_not_accept_empty_order_items():
    with pytest.raises(ValidationError) as exc_info:
        PurchaseInfo(())
    assert "order_items must not be empty" in str(exc_info.value)


def test_should_purchase_info_not_accept_duplicate_product_id():
    with pytest.raises(ValidationError) as exc_info:
        PurchaseInfo((OrderItem("p1", 3), OrderItem("p1", 4)))
    assert "order_items must not contain duplicate product_id" in str(exc_info.value)

    # won't raise error
    PurchaseInfo((OrderItem("p1", 3), OrderItem("p2", 4)))
