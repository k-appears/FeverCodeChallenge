import importlib
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.adapters.dependencies import (
    ProviderConfig,
    ProvidersConfig,
    get_providers_config,
)
from app.application.dtos.events import EventErrorDTO, ResponseEventDTO
from app.application.use_cases.request_events import RequestEventsUseCase
from app.infrastructure.database import RedisBase, create_redis_client
from app.infrastructure.repository.entities import FilterQuery

event_router = APIRouter()
log = logging.getLogger(__name__)

unix_start_date = datetime(1970, 1, 1)


@event_router.get(
    "/search",
    name="Lists the available events on a time range",
    response_model=ResponseEventDTO,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ResponseEventDTO,
            "content": {
                "application/json": {
                    "example": {"error": {"code": "string", "message": "string"}, "data": None},
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ResponseEventDTO,
            "content": {
                "application/json": {
                    "example": {"error": {"code": "string", "message": "string"}, "data": None},
                },
            },
        },
    },
)
async def get_events(
    starts_at: Annotated[
        datetime,
        Query(description="Return only events that starts after this date", example="2017-07-21T17:32:28Z"),
    ] = unix_start_date,
    ends_at: Annotated[
        datetime,
        Query(description="Return only events that finishes before this date", example="2021-07-21T17:32:28Z"),
    ] = datetime.now(),
    providers_config: ProvidersConfig = Depends(get_providers_config),
    redis: RedisBase = Depends(create_redis_client),
) -> ResponseEventDTO:
    starts_at = starts_at.replace(tzinfo=timezone.utc) if starts_at.tzinfo is None else starts_at
    ends_at = ends_at.replace(tzinfo=timezone.utc) if ends_at.tzinfo is None else ends_at
    if starts_at > ends_at:
        return ResponseEventDTO(
            data=None,
            error=EventErrorDTO(code=str(status.HTTP_400_BAD_REQUEST), message="starts_at must be less than ends_at"),
        )
    event_responses = [
        await _init_use_case(provider, redis).execute(FilterQuery(starts_at=starts_at, ends_at=ends_at))
        for provider in providers_config.external_providers
    ]
    return event_responses[0] if event_responses else ResponseEventDTO()  # Modify to adapt to multiple providers


def _init_use_case(provider: ProviderConfig, redis: RedisBase) -> RequestEventsUseCase:
    try:
        repository_module = importlib.import_module(provider.repository_module_path)
        return RequestEventsUseCase(getattr(repository_module, provider.class_name)(redis))
    except Exception as e:
        log.error(f"Invalid configuration: {e}", exc_info=True)
        raise ValueError(f"Class not found  {provider.class_name} in module {provider.repository_module_path}")
