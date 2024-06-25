from pydantic import Field, BaseModel

USER_INITIAL_BALANCE = 100


class User(BaseModel):
    id: str = Field(frozen=True)
    balance: float = Field(ge=0)
