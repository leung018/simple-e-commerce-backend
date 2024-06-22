from pydantic import Field, BaseModel


class User(BaseModel):
    id: str = Field(frozen=True)
    balance: float = Field(ge=0)
