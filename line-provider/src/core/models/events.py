import decimal

import sqlalchemy.orm as so

from src.core.models import Base
from src.core.schemas import Event as EventSchema
from src.core.schemas import EventState


class Event(Base):
    __tablename__ = "events"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    event_id: so.Mapped[str] = so.mapped_column(unique=True, nullable=False, index=True)
    coefficient: so.Mapped[decimal.Decimal] = so.mapped_column(nullable=False)
    deadline: so.Mapped[int] = so.mapped_column(nullable=False)
    state: so.Mapped[EventState] = so.mapped_column(nullable=False)

    def to_pydantic_schema(self) -> EventSchema:
        return EventSchema(
            id=self.id, event_id=self.event_id, coefficient=self.coefficient, deadline=self.deadline, state=self.state
        )
