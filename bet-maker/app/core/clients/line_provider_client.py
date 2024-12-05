import logging

import httpx
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.config import settings
from app.utils import get_logger

logger = get_logger(__file__, logging.DEBUG)


class LineProviderClient:
    async def get_active_events(self) -> list:
        try:
            async with httpx.AsyncClient() as client:
                url = f"{settings.URL}/api_v1/events/"
                response = await client.get(
                    url=url, params={"format": "json"}, headers={"Content-Type": "application/json"}, timeout=10
                )

        except (httpx.ConnectError, httpx.ConnectTimeout) as error:
            logger.error(f"Failed to connect to the server at {settings.URL}. Error: {error}")
            raise HTTPException(status_code=400, detail=f"Unable to fetch active events. Connection error: {error}")

        else:
            if response.is_error:
                logger.error(
                    f"Received error response from server: {response.status_code}. Content: {response.content.decode()}"
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch active events. Server returned status {response.status_code}",
                )
            events = jsonable_encoder(response.json())
            return events

    async def get_completed_events(self) -> list:
        try:
            async with httpx.AsyncClient() as client:
                url = f"{settings.URL}/api_v1/events/get_past_events"
                response = await client.get(
                    url=url, params={"format": "json"}, headers={"Content-Type": "application/json"}, timeout=10
                )

        except (httpx.ConnectError, httpx.ConnectTimeout) as error:
            logger.error(f"Failed to connect to the server at {settings.URL}. Error: {error}")
            raise HTTPException(status_code=400, detail=f"Unable to fetch completed events. Connection error: {error}")

        else:
            if response.is_error:
                logger.error(
                    f"Received error response from server: {response.status_code}. Content: {response.content.decode()}"
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch completed events. Server returned status {response.status_code}",
                )
            events = jsonable_encoder(response.json())
            return events
