import logging
import xml.etree.ElementTree as ET  # noqa
from typing import List, Optional

import httpx
import pybreaker
import tenacity
from httpx import TransportError
from pydantic import Field, ValidationError
from pydantic_core import PydanticSerializationError
from pydantic_xml import BaseXmlModel, ParsingError, attr, element

from app.domain.entities.event import AbstractEvent
from app.domain.entities.provider_a.provider_a import ProviderABaseEvent
from app.infrastructure.api.external_providers.base import BaseApiProvider


class Zone(BaseXmlModel):
    zone_id: int = attr()
    capacity: int = attr()
    price: float = attr()
    name: str = attr()
    numbered: bool = attr()


class Event(BaseXmlModel):
    event_start_date: str = attr()
    event_end_date: str = attr()
    event_id: str = attr()
    sell_from: str = attr()
    sell_to: str = attr()
    sold_out: bool = attr()
    zones: List[Zone] = element(tag="zone")


class BaseEvent(BaseXmlModel):
    base_event_id: str = attr()
    sell_mode: str = attr()
    title: str = attr()
    organizer_company_id: Optional[str] = attr(default=None)
    events: list[Event] = element(tag="event")


class Output(BaseXmlModel):
    base_events: list[BaseEvent] = Field(alias="base_event")


class EventList(BaseXmlModel, tag="eventList"):
    output: Output


log = logging.getLogger(__name__)


def is_400_error(exception: BaseException) -> bool:
    return isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code < 500


class ProviderA(BaseApiProvider):
    breaker = pybreaker.CircuitBreaker(fail_max=1, reset_timeout=60, exclude=[is_400_error])

    def __init__(self, provider_url: str) -> None:
        if not provider_url:
            raise ValueError("'conf.url' is not set or is empty in config.yml file")
        self._url = provider_url

    @breaker(__pybreaker_call_async=True)
    @tenacity.retry(
        reraise=True,
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        retry=(
            tenacity.retry_if_exception_type(TransportError)
            | tenacity.retry_if_exception(lambda exc: not is_400_error(exc))
        ),
    )
    async def extract(self) -> str:
        """
        :exception: HTTPStatusError, CircuitBreakerError
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self._url, follow_redirects=True, timeout=10)
            response.raise_for_status()
            return response.text

    async def parse(self, response: str) -> list[AbstractEvent]:
        if not response:
            raise ValueError("Response string is empty")
        try:
            events = EventList.from_xml(response.encode())
            return [ProviderABaseEvent(**base_event.model_dump()) for base_event in events.output.base_events]
        except (ET.ParseError, ParsingError) as parse_err:
            raise ValueError(f"XML Parsing Error: {parse_err}")
        except (ValidationError, PydanticSerializationError, ValueError) as value_err:
            raise ValueError(f"XML Validation Error: {value_err}")
