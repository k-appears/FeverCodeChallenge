from datetime import datetime
from typing import Sequence

from app.domain.entities.event import AbstractEvent
from app.infrastructure.api.external_providers.base import BaseApiProvider
from app.infrastructure.repository.base import BaseRepositoryProvider
from app.infrastructure.repository.entities import FilterQuery


class ProviderService:
    """Processing and storing events."""

    def __init__(self, api: BaseApiProvider, repository: BaseRepositoryProvider):
        self._repository = repository
        self._api = api

    async def extract_events(self) -> list[AbstractEvent]:
        response_str = await self._api.extract()
        return [event for event in await self._api.parse(response_str)]

    async def store_events(self, base_events: Sequence[AbstractEvent]) -> None:
        return await self._repository.add_or_update_events(base_events)

    async def retrieve_events(self, event_start: datetime, event_end: datetime) -> list[AbstractEvent]:
        return await self._repository.get_all(FilterQuery(starts_at=event_start, ends_at=event_end))
