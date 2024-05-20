from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from app.domain.entities.event import AbstractEvent


class SellModeEnum(str, Enum):
    online = "online"
    offline = "offline"


class ProviderAZone(BaseModel):
    zone_id: int = Field(description="Identifier for the zone")
    capacity: int = Field(description="Capacity of the zone")
    price: float = Field(description="Price of the zone")
    name: str = Field(description="Name of the zone")
    numbered: bool = Field(description="Zone is numbered or not")


class ProviderAEvent(BaseModel):
    event_id: int = Field(description="Identifier for the event")
    event_start_date: datetime = Field(description="Date when the event starts in local time")
    event_end_date: datetime = Field(description="Date when the event ends in local time")
    sell_from: datetime = Field(description="Date when the event starts to be sold")
    sell_to: datetime = Field(description="Date when the event stops to be sold")
    sold_out: bool = Field(description="Event is sold out or not")
    zones: list[ProviderAZone] = Field(description="List of zones for the event")

    @model_validator(mode="before")
    def start_date_must_be_before_end_date(
        cls,
        values: dict[str, Any],
    ) -> dict[str, Any]:  # Any used in official documentation
        date_format = "%Y-%m-%dT%H:%M:%S"
        event_start = values.get("event_start_date")
        event_end = values.get("event_end_date")
        if (
            event_end
            and event_start
            and isinstance(event_start, str)
            and isinstance(event_end, str)
            and datetime.strptime(event_start, date_format) >= datetime.strptime(event_end, date_format)
        ):
            raise ValueError("Event start date must be before event end date")
        return values


class ProviderABaseEvent(AbstractEvent):
    base_event_id: int = Field(description="Identifier for the base event")
    sell_mode: SellModeEnum = Field(description="Sell mode of the event")
    title: str = Field(description="Title of the plan")
    organizer_company_id: Optional[int] = Field(None, description="Identifier for the organizer company")
    events: list[ProviderAEvent] = Field(description="List of events for the base event")
