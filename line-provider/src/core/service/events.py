import time

from fastapi import HTTPException

from src.core.models import Event
from src.core.schemas import Event as EventSchema
from src.core.schemas import EventCreate, EventUpdate
from src.core.service.service import BaseService
from src.core.uow import UnitOfWork


class EventsService(BaseService):
    base_repository: str = "events"

    @classmethod
    async def __event_id_exist(cls, uow: UnitOfWork, event_id: str) -> bool:
        """
        Check if an event with the given event_id exists in the database.

        Parameters:
        uow (UnitOfWork): The UnitOfWork instance for database operations.
        event_id (str): The unique identifier of the event to check.

        Returns:
        bool: True if the event exists, False otherwise.
        """
        async with uow:
            result = await uow.__dict__[cls.base_repository].get_event_by_id(event_id=event_id)
        return True if result else False

    @classmethod
    async def get_all_active_events(cls, uow: UnitOfWork) -> list[EventSchema]:
        """
        Retrieve all active events from the database.

        This function fetches all events from the database that are currently active.
        An event is considered active if its state is set to 'active' and its deadline has not passed.

        Parameters:
        uow (UnitOfWork): The UnitOfWork instance for database operations.
        This instance provides a context manager for managing database transactions.

        Returns:
        list[EventSchema]: A list of EventSchema objects representing the active events.
        Each EventSchema object is a Pydantic model that corresponds to the Event model.
        """
        async with uow:
            result = await uow.__dict__[cls.base_repository].get_all_active_events()
        events = [event.to_pydantic_schema() for event in result]
        return events

    @classmethod
    async def get_event_by_id(cls, uow: UnitOfWork, event_id: str) -> EventSchema:
        """
        Retrieve an event by its unique identifier from the database.

        This function fetches an event from the database using the provided event_id.
        If the event is not found, it raises a 404 HTTPException.

        Parameters:
        uow (UnitOfWork): The UnitOfWork instance for database operations.
        This instance provides a context manager for managing database transactions.

        event_id (str): The unique identifier of the event to retrieve.

        Returns:
        EventSchema: A Pydantic model representing the retrieved event.
        Each EventSchema object corresponds to the Event model.
        If the event is not found, it raises a 404 HTTPException.
        """
        async with uow:
            result = await uow.__dict__[cls.base_repository].get_event_by_id(event_id=event_id)
            if not result:
                raise HTTPException(status_code=404, detail=f"Event with event_id {event_id} not found!")
        event = result.to_pydantic_schema()
        return event

    @classmethod
    async def get_past_events(cls, uow: UnitOfWork) -> list[EventSchema]:
        """
        Retrieve all past events from the database.

        This function fetches all events from the database that have already passed their deadline.
        An event is considered past if its deadline has already passed.

        Parameters:
        uow (UnitOfWork): The UnitOfWork instance for database operations.
        This instance provides a context manager for managing database transactions.

        Returns:
        list[EventSchema]: A list of EventSchema objects representing the past events.
        Each EventSchema object corresponds to the Event model.
        """
        current_time = time.time()
        async with uow:
            result = await uow.__dict__[cls.base_repository].get_past_events(current_time=current_time)
        events = [event.to_pydantic_schema() for event in result]
        return events

    @classmethod
    async def create_event(cls, uow: UnitOfWork, event: EventCreate) -> EventSchema:
        """
        Creates a new event in the database.

        This function checks if an event with the same event_id already exists in the database.
        If the event_id is unique, it creates a new Event model instance using the provided EventCreate schema,
        sets the deadline as the current time plus the provided deadline, and inserts the event into the database.
        If the event_id already exists, it raises a 400 HTTPException.

        Parameters:
        uow (UnitOfWork): The UnitOfWork instance for database operations.
        event (EventCreate): A Pydantic model representing the new event to be created.

        Returns:
        EventSchema: A Pydantic model representing the newly created event.
        """
        if await cls.__event_id_exist(uow=uow, event_id=event.event_id):
            raise HTTPException(status_code=400, detail=f"Event with event_id {event.event_id} already exists!")
        event_model = Event(
            event_id=event.event_id,
            coefficient=event.coefficient,
            deadline=int(time.time() + event.deadline),
            state=event.state,
        )
        async with uow:
            result = await uow.__dict__[cls.base_repository].create_event(event=event_model)
        created_event = result.to_pydantic_schema()
        return created_event

    @classmethod
    async def update_event(cls, event_id: str, event: EventUpdate, uow: UnitOfWork) -> EventSchema:
        """
        Updates an existing event in the database.

        This function takes an event_id, an EventUpdate schema, and a UnitOfWork instance as parameters.
        It first checks if an event with the given event_id exists in the database.
        If the event exists, it updates the event's attributes with the provided EventUpdate schema.
        If the event does not exist, it raises a 404 HTTPException.

        Parameters:
        event_id (str): The unique identifier of the event to update.
        event (EventUpdate): A Pydantic model representing the updated event data.
        uow (UnitOfWork): The UnitOfWork instance for database operations.

        Returns:
        EventSchema: A Pydantic model representing the updated event.
        """
        async with uow:
            result = await uow.__dict__[cls.base_repository].update_event(event_id=event_id, event=event)
            if not result:
                raise HTTPException(status_code=404, detail=f"Event with event_id {event_id} not found!")
        updated_event = result.to_pydantic_schema()
        return updated_event

    @classmethod
    async def delete_event(cls, event_id: str, uow: UnitOfWork) -> None:
        """
        Deletes an event from the database using the provided event_id.

        This function first checks if an event with the given event_id exists in the database.
        If the event exists, it deletes the event from the database.
        If the event does not exist, it raises a 404 HTTPException.

        Parameters:
        event_id (str): The unique identifier of the event to delete.
        uow (UnitOfWork): The UnitOfWork instance for database operations.

        Returns:
        None: This function does not return any value.
        """
        if not await cls.__event_id_exist(uow=uow, event_id=event_id):
            raise HTTPException(status_code=404, detail=f"Event with event_id {event_id} not found!")
        async with uow:
            await uow.__dict__[cls.base_repository].delete_event(event_id=event_id)
