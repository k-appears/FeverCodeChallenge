import sys

from app.application.dtos.events import EventDTO, EventsDTO, ResponseEventDTO
from app.domain.entities.event import AbstractEvent
from app.domain.entities.provider_a.provider_a import ProviderABaseEvent


def map_provider_events_to_response_dto(base_events: list[AbstractEvent]) -> ResponseEventDTO:
    events_data = []
    for base_event in base_events:
        if not isinstance(base_event, ProviderABaseEvent):
            continue
        for event in base_event.events:
            min_price = sys.float_info.max
            max_price = sys.float_info.min
            for zone in event.zones:
                if zone.price < min_price:
                    min_price = zone.price
                if zone.price > max_price:
                    max_price = zone.price

            event_data = EventDTO(
                id=str(base_event.base_event_id),
                title=base_event.title,
                start_date=event.event_start_date.date(),
                start_time=event.event_start_date.time(),
                end_date=event.event_end_date.date(),
                end_time=event.event_end_date.time(),
                min_price=min_price,
                max_price=max_price,
            )
            events_data.append(event_data)

    return ResponseEventDTO(data=EventsDTO(events=events_data))
