from uuid import UUID, uuid4
from pydantic.dataclasses import dataclass
from pydantic import Field, field_validator


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int = Field(gt=0)


@dataclass(frozen=True)
class PurchaseInfo:
    order_items: tuple[OrderItem, ...]

    # Expect this id is generate from client side so that can prevent duplicate order.
    # The validation of format of this id from client side is in PurchaseRequest.
    # Use str here because business logic doesn't care about the format of this id and can make code and test in domain layer simpler.
    order_id: str

    @field_validator("order_items")
    @classmethod
    def validate_order_items(cls, v: tuple[OrderItem, ...]):
        if len(v) == 0:
            raise ValueError("order_items must not be empty")

        seen_product_ids = set()
        for item in v:
            if item.product_id in seen_product_ids:
                raise ValueError("order_items must not contain duplicate product_id")
            seen_product_ids.add(item.product_id)

        return v


@dataclass(frozen=True)
class Order:
    id: str
    user_id: str
    order_items: tuple[OrderItem, ...]
