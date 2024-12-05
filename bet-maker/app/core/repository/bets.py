from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app.core.models import Bet
from app.core.repository.repository import SqlAlchemyRepository
from app.core.schemas import BetState


class BetsRepository(SqlAlchemyRepository):
    model = Bet

    async def calculate_bets(self, completed_events: dict) -> None:
        """
        Update the status of bets based on the results of completed events.

        Parameters:
        completed_events (dict): A dictionary where keys are event IDs and values are the corresponding event results.

        Returns:
        None: This function does not return any value. It updates the status of bets in the database.
        """
        query = await self.session.execute(select(Bet).filter_by(status=BetState.NEW))
        bets = query.scalars().all()
        updated_bets = []

        for bet in bets:
            event_result = completed_events.get(bet.event_id)
            if event_result:
                bet.status = BetState.FINISHED_WIN if event_result == "2" else BetState.FINISHED_LOSE
                updated_bets.append(bet)

        self.session.add_all(updated_bets)

    async def get_all_bets(self) -> Sequence[Bet]:
        """
        Retrieve all bets from the database.

        This function executes a SQL query to select all records from the 'bets' table.
        It then fetches and returns the result as a list of Bet objects.

        Parameters:
        None: This function does not take any parameters.

        Returns:
        Sequence[Bet]: A list of Bet objects representing all bets in the database.
        """
        query = select(Bet)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bet_by_event_id(self, event_id: str) -> Bet | None:
        """
        Retrieve a bet from the database based on the provided event ID.

        This function executes a SQL query to select a single record from the 'bets' table
        where the 'event_id' column matches the provided 'event_id' parameter.

        Parameters:
        event_id (str): The unique identifier of the event for which the bet is being retrieved.

        Returns:
        Bet | None: The retrieved Bet object if a match is found, or None if no match is found.
        """
        query = await self.session.execute(select(Bet).filter_by(event_id=event_id))
        try:
            result = query.scalars().one()
            return result
        except NoResultFound:
            return None

    async def create_bet(self, bet: Bet) -> Bet:
        """
        Create a new bet in the database.

        This function takes a Bet object as input and inserts it into the 'bets' table in the database.
        It uses an asynchronous context manager to handle the database transaction.

        Parameters:
        bet (Bet): The Bet object to be inserted into the database. The object must have all required attributes set.

        Returns:
        Bet: The same Bet object that was passed as input. This object is now stored in the database.
        """
        async with self.session.begin():
            self.session.add(bet)
        return bet
