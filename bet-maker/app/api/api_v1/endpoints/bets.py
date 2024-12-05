from fastapi import APIRouter, Depends

from app.core.clients import LineProviderClient
from app.core.schemas import Bet, BetCreate
from app.core.service.bets import BetsService
from app.core.uow import UnitOfWork

router = APIRouter()


@router.get("/events", status_code=200, response_model=list)
async def get_all_events(
    line_provider_client: LineProviderClient = Depends(LineProviderClient),
) -> list:
    """
    Retrieve all active events from the line provider.

    Parameters:
    line_provider_client (LineProviderClient): The client used to interact with the line provider service.

    Returns:
    list: A list of active events.
    """
    return await BetsService.get_active_events(line_provider_client=line_provider_client)


@router.get("/bets", status_code=200, response_model=list[Bet])
async def get_bet_history(
    uow: UnitOfWork = Depends(UnitOfWork), line_provider_client: LineProviderClient = Depends(LineProviderClient)
) -> list[Bet]:
    """
    Retrieve the history of bets.

    Parameters:
    uow (UnitOfWork): The unit of work used to manage database transactions.
    line_provider_client (LineProviderClient): The client used to interact with the line provider service.

    Returns:
    list[Bet]: A list of Bet objects representing the bet history.
    """
    return await BetsService.get_bet_history(uow=uow, line_provider_client=line_provider_client)


@router.post("/bet", status_code=201, response_model=Bet)
async def create_bet(
        bet: BetCreate,
        uow: UnitOfWork = Depends(UnitOfWork),
        line_provider_client: LineProviderClient = Depends(LineProviderClient)
) -> Bet:
    """
    Create a new bet.

    This function is responsible for creating a new bet based on the provided BetCreate object.
    It interacts with the UnitOfWork to manage database transactions
    and the BetsService to perform the actual bet creation.

    Parameters:
    bet (BetCreate): A BetCreate object containing the necessary information to create a new bet.
    uow (UnitOfWork): The unit of work used to manage database transactions.
    line_provider_client (LineProviderClient): The client used to interact with the line provider service.

    Returns:
    Bet: A Bet object representing the newly created bet.
    """
    return await BetsService.create_bet(bet=bet, uow=uow, line_provider_client=line_provider_client)
