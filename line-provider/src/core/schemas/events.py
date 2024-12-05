import decimal
import enum

from pydantic import BaseModel, PositiveInt


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class EventBase(BaseModel):
    event_id: str
    coefficient: decimal.Decimal
    deadline: int
    state: EventState


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventInDB(EventBase):
    id: PositiveInt

    class Config:
        from_attributes = True


class Event(EventInDB):
    pass
