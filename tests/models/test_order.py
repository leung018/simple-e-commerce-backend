from pydantic import ValidationError
import pytest
from app.models.order import Order


def test_should_order_not_accept_empty_product_ids():
    with pytest.raises(ValidationError) as exc_info:
        Order(id="o1", user_id="u1", product_ids=frozenset())
    assert "product_ids must not be empty" in str(exc_info.value)
