from abc import ABC, abstractmethod

from app.domain.entities.event import AbstractEvent


class BaseApiProvider(ABC):
    """Strategy pattern for external providers"""

    @abstractmethod
    async def extract(self) -> str:
        pass

    @abstractmethod
    async def parse(self, response: str) -> list[AbstractEvent]:
        pass
