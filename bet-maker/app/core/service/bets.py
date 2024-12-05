from fastapi import HTTPException

from app.core.clients import LineProviderClient
from app.core.models import Bet
from app.core.schemas import Bet as BetSchema
from app.core.schemas import BetCreate
from app.core.service.service import BaseService
from app.core.uow import UnitOfWork


class BetsService(BaseService):
    base_repository: str = "bets"

    @classmethod
    async def __event_id_exist(cls, line_provider_client: LineProviderClient, event_id: str) -> bool:
        """
        Check if an event with the given event_id exists.

        Parameters:
        line_provider_client (LineProviderClient): An instance of LineProviderClient for making API calls.
        event_id (str): The unique identifier of the event.

        Returns:
        bool: True if an event with the given event_id exists, False otherwise.
        """
        events_list = await line_provider_client.get_active_events()
        result = any(event["event_id"] == event_id for event in events_list)
        return True if result else False

    @classmethod
    async def __bet_event_id_exist(cls, uow: UnitOfWork, event_id: str) -> bool:
        """
        Check if a bet with the given event_id exists in the database.

        Parameters:
        uow (UnitOfWork): An instance of UnitOfWork for database operations.
        event_id (str): The unique identifier of the event for which to check the existence of a bet.

        Returns:
        bool: True if a bet with the given event_id exists, False otherwise.
        """
        async with uow:
            result = await uow.__dict__[cls.base_repository].get_bet_by_event_id(event_id=event_id)
        return True if result else False

    @classmethod
    async def __get_completed_events(cls, line_provider_client: LineProviderClient) -> dict:
        """
        Fetch completed events from the LineProviderClient and return them as a dictionary.

        Parameters:
        line_provider_client (LineProviderClient): An instance of LineProviderClient for making API calls.

        Returns:
        dict: A dictionary where the keys are event_ids and the values are the corresponding event states.
        """
        events_list = await line_provider_client.get_completed_events()
        events_dict = {event["event_id"]: event["state"] for event in events_list}
        return events_dict

    @classmethod
    async def __calculate_bets(cls, uow: UnitOfWork, line_provider_client: LineProviderClient) -> None:
        """
        Calculate bets based on completed events fetched from the LineProviderClient.

        This function fetches completed events from the LineProviderClient, retrieves the corresponding
        bets from the database, and updates the bets' status based on the event states.

        Parameters:
        uow (UnitOfWork): An instance of UnitOfWork for database operations.
        line_provider_client (LineProviderClient): An instance of LineProviderClient for making API calls.

        Returns:
        None: This function is asynchronous and does not return any value.
        """
        completed_events = await cls.__get_completed_events(line_provider_client=line_provider_client)
        async with uow:
            await uow.__dict__[cls.base_repository].calculate_bets(completed_events=completed_events)

    @classmethod
    async def get_active_events(cls, line_provider_client: LineProviderClient) -> list:
        """
        Fetch and return a list of active events from the LineProviderClient.

        Parameters:
        line_provider_client (LineProviderClient): An instance of LineProviderClient for making API calls.

        Returns:
        list: A list of dictionaries representing active events. Each dictionary contains event-specific information.
        """
        return await line_provider_client.get_active_events()

    @classmethod
    async def get_bet_history(cls, uow: UnitOfWork, line_provider_client: LineProviderClient) -> list[BetSchema]:
        """
        Fetch and return a list of bets from the database, including their calculated status based on completed events.

        This function first calls the __calculate_bets method to update the bets' status
        based on completed events fetched from the LineProviderClient.
        Then, it retrieves all bets from the database and returns them as a list of BetSchema objects.

        Parameters:
        uow (UnitOfWork): An instance of UnitOfWork for database operations.
        line_provider_client (LineProviderClient): An instance of LineProviderClient for making API calls.

        Returns:
        list[BetSchema]: A list of BetSchema objects representing bets.
        Each BetSchema object contains bet-specific information.
        """
        await cls.__calculate_bets(uow=uow, line_provider_client=line_provider_client)
        async with uow:
            result = await uow.__dict__[cls.base_repository].get_all_bets()
        bets = [bet.to_pydantic_schema() for bet in result]
        return bets

    @classmethod
    async def create_bet(cls, uow: UnitOfWork, bet: BetCreate, line_provider_client: LineProviderClient) -> BetSchema:
        """
        Create a new bet in the database.

        This function checks if an event with event_id exist and
        if a bet with the same event_id already exists in the database.
        If it does, it raises an HTTPException with a 400 status code and a descriptive error message.
        Otherwise, it creates a new Bet model instance using the provided BetCreate schema,
        saves it to the database, and returns the created BetSchema object.

        Parameters:
        uow (UnitOfWork): An instance of UnitOfWork for database operations.
        bet (BetCreate): A BetCreate schema object containing the necessary information for creating a new bet.

        Returns:
        BetSchema: A BetSchema object representing the newly created bet.
        """
        if not await cls.__event_id_exist(line_provider_client=line_provider_client, event_id=bet.event_id):
            raise HTTPException(status_code=400, detail=f"Event with event_id {bet.event_id} does not exists!")
        if await cls.__bet_event_id_exist(uow=uow, event_id=bet.event_id):
            raise HTTPException(status_code=400, detail=f"Bet with event_id {bet.event_id} already exists!")
        bet_model = Bet(bet_id=bet.bet_id, event_id=bet.event_id, amount=bet.amount, status=bet.status)
        async with uow:
            result = await uow.__dict__[cls.base_repository].create_bet(bet=bet_model)
        created_bet = result.to_pydantic_schema()
        return created_bet
