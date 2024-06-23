from pydantic.dataclasses import dataclass
from pydantic import field_validator


@dataclass(frozen=True)
class Order:
    id: str
    user_id: str
    product_ids: tuple[str, ...]

    @field_validator("product_ids")
    @classmethod
    def check_product_ids_not_empty(cls, v: tuple):
        if len(v) == 0:
            raise ValueError("product_ids must not be empty")
        return v
