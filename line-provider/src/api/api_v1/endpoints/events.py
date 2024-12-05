from fastapi import APIRouter, Depends

from src.core.schemas import Event, EventCreate, EventUpdate
from src.core.service.events import EventsService
from src.core.uow import UnitOfWork

router = APIRouter()


@router.get("/", status_code=200, response_model=list[Event])
async def get_all_active_events(uow: UnitOfWork = Depends(UnitOfWork)) -> list[Event]:
    """
    Retrieves all active events.

    Parameters:
    uow (UnitOfWork): A dependency injection for UnitOfWork,
    which provides a single database session for the entire request.

    Returns:
    list[Event]: A list of active Event objects.
    """
    return await EventsService.get_all_active_events(uow=uow)


@router.get("/get_event", status_code=200, response_model=Event)
async def get_event_by_id(event_id: str, uow: UnitOfWork = Depends(UnitOfWork)) -> Event:
    """
    Retrieves a single event by its ID.

    Parameters:
    event_id (str): The unique identifier of the event to retrieve.
    uow (UnitOfWork): A dependency injection for UnitOfWork,
    which provides a single database session for the entire request.

    Returns:
    Event: The requested Event object.
    """
    return await EventsService.get_event_by_id(uow=uow, event_id=event_id)


@router.get("/get_past_events", status_code=200, response_model=list[Event])
async def get_past_events(uow: UnitOfWork = Depends(UnitOfWork)) -> list[Event]:
    """
    Retrieves a list of past events.

    This function is responsible for fetching all events that have already occurred.
    It uses the provided UnitOfWork (uow) to interact with the database.

    Parameters:
    uow (UnitOfWork): A dependency injection for UnitOfWork,
    which provides a single database session for the entire request.

    Returns:
    list[Event]: A list of Event objects representing past events.
    """
    return await EventsService.get_past_events(uow=uow)


@router.post("/create_event", status_code=201, response_model=Event)
async def create_event(event: EventCreate, uow: UnitOfWork = Depends(UnitOfWork)) -> Event:
    """
    Creates a new event in the system.

    This function accepts an EventCreate object representing the details of the new event.
    It uses the provided UnitOfWork (uow) to interact with the database and create a new record.

    Parameters:
    event (EventCreate): An object containing the details of the new event.
        This object should be validated against the EventCreate schema.
    uow (UnitOfWork): A dependency injection for UnitOfWork,
        which provides a single database session for the entire request.

    Returns:
    Event: The newly created Event object.
        This object will be validated against the Event schema.
    """
    return await EventsService.create_event(event=event, uow=uow)


@router.put("/update_event", status_code=201, response_model=Event)
async def update_event(event_id: str, event: EventUpdate, uow: UnitOfWork = Depends(UnitOfWork)) -> Event:
    """
    Updates an existing event in the system.

    This function accepts an event_id and an EventUpdate object representing the updated details of the event.
    It uses the provided UnitOfWork (uow) to interact with the database and update the existing record.

    Parameters:
    event_id (str): The unique identifier of the event to update.
    event (EventUpdate): An object containing the updated details of the event.
        This object should be validated against the EventUpdate schema.
    uow (UnitOfWork): A dependency injection for UnitOfWork,
        which provides a single database session for the entire request.

    Returns:
    Event: The updated Event object.
        This object will be validated against the Event schema.
    """
    return await EventsService.update_event(event_id=event_id, event=event, uow=uow)


@router.delete("/delete_event/{event_id}", status_code=204)
async def delete_event(event_id: str, uow: UnitOfWork = Depends(UnitOfWork)) -> None:
    """
    Deletes an existing event from the system.

    This function accepts an event_id and uses the provided UnitOfWork (uow)
    to interact with the database and delete the corresponding record.

    Parameters:
    event_id (str): The unique identifier of the event to delete.
        This parameter is expected to be a non-empty string.
    uow (UnitOfWork): A dependency injection for UnitOfWork,
        which provides a single database session for the entire request.
        This parameter is expected to be an instance of UnitOfWork.

    Returns:
    None: This function does not return any value.
    """
    return await EventsService.delete_event(event_id=event_id, uow=uow)
