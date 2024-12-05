import decimal

import sqlalchemy.orm as so

from app.core.models import Base
from app.core.schemas import Bet as BetSchema
from app.core.schemas import BetState


class Bet(Base):
    __tablename__ = "bets"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    bet_id: so.Mapped[str] = so.mapped_column(unique=True, nullable=False, index=True)
    event_id: so.Mapped[str] = so.mapped_column(nullable=False, index=True)
    amount: so.Mapped[decimal.Decimal] = so.mapped_column(nullable=False)
    status: so.Mapped[BetState] = so.mapped_column(nullable=False)

    def to_pydantic_schema(self) -> BetSchema:
        return BetSchema(id=self.id, bet_id=self.bet_id, event_id=self.event_id, amount=self.amount, status=self.status)
