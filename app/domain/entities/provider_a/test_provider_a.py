import pytest

from app.domain.entities.provider_a.provider_a import ProviderAEvent


def test_start_date_must_be_before_end_date():
    parameters = {
        "event_id": 1,
        "event_start_date": "2021-07-31T20:00:00",
        "event_end_date": "2021-07-31T20:00:00",
        "sell_from": "2021-01-01T00:00:00",
        "sell_to": "2021-01-01T00:00:00",
        "sold_out": False,
        "zones": [{"zone_id": 1, "capacity": 100, "price": 10.0, "name": "Zone 1", "numbered": True}],
    }

    with pytest.raises(ValueError) as exc_info:
        ProviderAEvent(**parameters)

    assert "Event start date must be before event end date" in str(exc_info.value)
