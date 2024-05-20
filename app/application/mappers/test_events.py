from datetime import datetime

import pytest

from app.application.mappers.events import map_provider_events_to_response_dto
from app.domain.entities.provider_a.provider_a import (
    ProviderABaseEvent,
    ProviderAEvent,
    ProviderAZone,
    SellModeEnum,
)


@pytest.fixture
def sample_provider_event():
    event_data = {
        "base_event_id": 1,
        "title": "Sample Event",
        "sell_mode": SellModeEnum.online,
        "event_start_date": datetime(2024, 5, 8, 10, 0),
        "event_end_date": datetime(2024, 5, 8, 12, 0),
        "events": [
            {
                "event_id": 1,
                "event_start_date": datetime(2024, 5, 8, 10, 0),
                "event_end_date": datetime(2024, 5, 8, 12, 0),
                "sell_from": datetime(2024, 5, 1, 0, 0),
                "sell_to": datetime(2024, 5, 7, 23, 59),
                "sold_out": False,
                "zones": [
                    {"zone_id": 1, "capacity": 100, "price": 50.0, "name": "Zone A", "numbered": True},
                    {"zone_id": 2, "capacity": 100, "price": 75.0, "name": "Zone B", "numbered": True},
                ],
            },
        ],
    }
    return [ProviderABaseEvent(**event_data)]


def test_map_provider_to_response_happy_path(sample_provider_event):
    response = map_provider_events_to_response_dto(sample_provider_event)
    assert response.error is None
    assert len(response.data.events) == 1
    assert response.data.events[0].id == "1"
    assert response.data.events[0].title == "Sample Event"
    assert response.data.events[0].min_price == 50.0
    assert response.data.events[0].max_price == 75.0


def test_map_provider_to_response_happy_path_empty():
    empty_zones_event = ProviderABaseEvent(
        base_event_id=1,
        title="Empty Zones Event",
        events=[],
        sell_mode=SellModeEnum.online,
        organizer_company_id=1,
    )
    response = map_provider_events_to_response_dto([empty_zones_event])
    assert len(response.data.events) == 0
    assert response.error is None


def test_map_provider_to_response_single_zone():
    single_zone_event = ProviderABaseEvent(
        base_event_id=1,
        sell_mode=SellModeEnum.online,
        title="Single Zone Event",
        events=[
            ProviderAEvent(
                event_id=1000,
                event_start_date=datetime(2024, 5, 8, 10, 0),
                event_end_date=datetime(2024, 5, 8, 12, 0),
                sell_from=datetime(2024, 5, 1, 0, 0),
                sell_to=datetime(2024, 5, 7, 23, 59),
                sold_out=False,
                zones=[ProviderAZone(zone_id=1, capacity=100, price=50.0, name="Zone A", numbered=True)],
            ),
        ],
    )
    response = map_provider_events_to_response_dto([single_zone_event])
    assert response.error is None
    assert len(response.data.events) == 1
    assert response.data.events[0].min_price == 50.0
    assert response.data.events[0].max_price == 50.0
    assert response.data.events[0].title == "Single Zone Event"
    assert response.data.events[0].id == "1"
