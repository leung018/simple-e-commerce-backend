from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: str
    user_id: str
    product_ids: tuple[str, ...]
