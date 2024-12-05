import random
import time
from typing import Sequence

from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound

from src.core.models import Event
from src.core.repository.repository import SqlAlchemyRepository
from src.core.schemas import EventState, EventUpdate


class EventsRepository(SqlAlchemyRepository):
    model = Event

    async def __calculate_results(self, current_time: int) -> None:
        """
        This function calculates the results of past events that have not been processed yet.
        It updates the state of these events to either FINISHED_WIN or FINISHED_LOSE randomly.

        Parameters:
        current_time (int): The current time in Unix timestamp format. This is used to determine
                            which events have passed their deadline.

        Returns:
        None: This function does not return any value. It updates the state of events in the database.
        """
        async with self.session.begin():
            base_query = select(self.model).filter(
                (self.model.deadline < current_time) & (self.model.state == EventState.NEW)
            )
            query = await self.session.execute(base_query.order_by(desc(self.model.deadline)))
            events = query.scalars().all()
            for event in events:
                event.state = random.choice([EventState.FINISHED_WIN, EventState.FINISHED_LOSE])

    async def get_all_active_events(self) -> Sequence[Event]:
        """
        Retrieves all active events from the database.

        Active events are those with a deadline greater than the current time.

        Parameters:
        None

        Returns:
        Sequence[Event]: A sequence of Event objects representing the active events.
        """
        base_query = select(self.model).filter(self.model.deadline > time.time())
        query = await self.session.execute(base_query)
        results = query.scalars().all()
        return results

    async def get_event_by_id(self, event_id: str) -> Event | None:
        """
        Retrieves a single event from the database based on its unique identifier.

        Parameters:
        event_id (str): The unique identifier of the event to retrieve.

        Returns:
        Event | None: The retrieved event object if found, or None if no event with the given ID exists.
        """
        query = await self.session.execute(select(Event).filter_by(event_id=event_id))
        try:
            result = query.scalars().one()
            return result
        except NoResultFound:
            return None

    async def get_past_events(self, current_time: int) -> Sequence[Event]:
        """
        Retrieves past events from the database and updates their results if necessary.

        This function first calls the private method `__calculate_results` to update the results of
        past events that have not been processed yet. It then retrieves all past events from the
        database, ordered by their deadline in descending order.

        Parameters:
        current_time (int): The current time in Unix timestamp format. This is used to determine
                            which events have passed their deadline.

        Returns:
        Sequence[Event]: A sequence of Event objects representing the past events.
        """
        await self.__calculate_results(current_time=current_time)
        async with self.session.begin():
            base_query = select(self.model).filter(self.model.deadline < current_time)
            query = await self.session.execute(base_query.order_by(desc(self.model.deadline)))
            results = query.scalars().all()
        return results

    async def create_event(self, event: Event) -> Event:
        """
        Creates a new event in the database.

        This function takes an Event object as input and adds it to the database.
        It uses an asynchronous context manager (async with) to handle database transactions.

        Parameters:
        event (Event): The Event object to be created in the database. This object should
                       contain all the necessary information for the event, such as its
                       unique identifier, title, description, deadline, and state.

        Returns:
        Event: The newly created Event object. This object will have its unique identifier
               populated by the database.
        """
        async with self.session.begin():
            self.session.add(event)
        return event

    async def update_event(self, event_id: str, event: EventUpdate) -> Event | None:
        """
        Updates an existing event in the database based on its unique identifier.

        This function takes an event ID and an EventUpdate object as input. It retrieves the
        corresponding event from the database, updates its attributes with the provided values,
        and commits the changes to the database.

        Parameters:
        event_id (str): The unique identifier of the event to be updated.
        event (EventUpdate): An object containing the updated attributes for the event.
                             The object should only contain the attributes that need to be updated.
                             Any attributes not present in the object will not be modified.

        Returns:
        Event | None: The updated Event object if the event was found and updated successfully.
                      Returns None if no event with the given ID was found in the database.
        """
        async with self.session.begin():
            query = await self.session.execute(select(Event).filter_by(event_id=event_id))
            try:
                db_event = query.scalars().one()
                for field, value in event.dict(exclude_unset=True).items():
                    setattr(db_event, field, value)
            except NoResultFound:
                return None
        return db_event

    async def delete_event(self, event_id: str) -> None:
        """
        Deletes an event from the database based on its unique identifier.

        This function takes an event ID as input, retrieves the corresponding event from the database,
        and deletes it from the database. It uses an asynchronous context manager (async with) to handle
        database transactions.

        Parameters:
        event_id (str): The unique identifier of the event to be deleted.

        Returns:
        None: This function does not return any value. It deletes the event from the database.
        """
        async with self.session.begin():
            query = await self.session.execute(select(Event).filter_by(event_id=event_id))
            db_event = query.scalars().one()
            await self.session.delete(db_event)
