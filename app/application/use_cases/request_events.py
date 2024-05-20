from starlette import status

from app.application.dtos.events import EventErrorDTO, ResponseEventDTO
from app.application.mappers.events import map_provider_events_to_response_dto
from app.infrastructure.repository.base import BaseRepositoryProvider
from app.infrastructure.repository.entities import DatabaseError, FilterQuery


class ResultEvent:
    pass


class RequestEventsUseCase:
    def __init__(self, repository: BaseRepositoryProvider) -> None:
        self._repository = repository

    async def execute(self, filter_query: FilterQuery) -> ResponseEventDTO:
        try:
            events = await self._repository.get_all(filter_query)
            return map_provider_events_to_response_dto(events)
        except (DatabaseError, Exception) as e:
            return ResponseEventDTO(
                error=EventErrorDTO(code=str(status.HTTP_500_INTERNAL_SERVER_ERROR), message=str(e)),
            )
