import enum
from decimal import ROUND_DOWN, Decimal
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, field_validator


class BetState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class BetBase(BaseModel):
    bet_id: str
    event_id: str
    amount: Decimal = Field(..., gt=0, description="Bet amount, must be a strictly positive number")
    status: Optional[BetState]

    @field_validator("amount")
    def validate_decimal_places(cls, value):
        amount = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        if amount != Decimal(value):
            raise ValueError("The amount must have no more than two decimal places")
        return amount


class BetCreate(BetBase):
    pass


class BetUpdate(BetBase):
    pass


class BetInDB(BetBase):
    id: PositiveInt

    class Config:
        from_attributes = True


class Bet(BetInDB):
    pass
