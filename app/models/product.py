from pydantic import Field, BaseModel


class Product(BaseModel):
    id: str = Field(frozen=True)
    name: str
    category: str
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)
