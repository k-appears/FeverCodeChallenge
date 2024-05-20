from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.event import AbstractEvent
from app.infrastructure.repository.entities import FilterQuery


class BaseRepositoryProvider(ABC):
    @abstractmethod
    async def add_or_update_events(self, base_events: Sequence[AbstractEvent]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, filter_query: FilterQuery) -> list[AbstractEvent]:
        raise NotImplementedError
