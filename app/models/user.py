from pydantic import Field, BaseModel


class User(BaseModel):
    id: str = Field(frozen=True)
    balance: int = Field(ge=0)
