import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.event import AbstractEvent
from app.domain.entities.provider_a.provider_a import ProviderABaseEvent, SellModeEnum
from app.domain.services.provider_a import ProviderService
from app.infrastructure.api.external_providers.base import BaseApiProvider
from app.infrastructure.repository.base import BaseRepositoryProvider
from app.infrastructure.repository.entities import DatabaseError

log = logging.getLogger(__name__)


class ResultStatus(Enum):
    OK = "OK"
    ERROR = "ERROR"


class ResultUpdateProvider(BaseModel):
    status: ResultStatus
    error_description: Optional[str] = None


class UpdateEventsUseCase:
    def __init__(self, api: BaseApiProvider, repository: BaseRepositoryProvider):
        self._event_service = ProviderService(api, repository)

    async def execute(self) -> ResultUpdateProvider:
        """
        1. Obtain all the events from the providers
        2. Filter the provider A events that the sell mode is 'online'
        3. Store the events
        :return: status of the operation
        """
        try:
            events = await self._event_service.extract_events()
            online_events = self._filter_online_events(events)
            await self._event_service.store_events(online_events)
            return ResultUpdateProvider(status=ResultStatus.OK)
        except (ValueError, DatabaseError, Exception) as e:
            log.error(f"Error updating events: {e}", exc_info=True)
            return ResultUpdateProvider(status=ResultStatus.ERROR, error_description="Error updating events")

    @staticmethod
    def _filter_online_events(events: list[AbstractEvent]) -> list[ProviderABaseEvent]:
        result = [
            base_event
            for base_event in events
            if isinstance(base_event, ProviderABaseEvent) and base_event.sell_mode == SellModeEnum.online
        ]
        return result
