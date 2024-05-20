import json

from app.domain.entities.provider_a.provider_a import (
    ProviderABaseEvent,
    ProviderAEvent,
    SellModeEnum,
)
from app.domain.services.provider_a import ProviderService
from app.infrastructure.api.external_providers.base import BaseApiProvider
from app.infrastructure.repository.base import BaseRepositoryProvider


async def test_retrieve_all_events(mocker):
    repository = mocker.Mock(spec_set=BaseRepositoryProvider)
    api = mocker.Mock(spec_set=BaseApiProvider)
    parameters = {
        "event_id": 1,
        "event_start_date": "2021-01-01T21:00:00",
        "event_end_date": "2021-01-02T23:00:00",
        "sell_from": "2021-01-01T00:00:00",
        "sell_to": "2021-01-02T00:00:00",
        "sold_out": False,
        "zones": [],
    }
    event_a = ProviderAEvent(**parameters)
    base_event = ProviderABaseEvent(
        base_event_id=1,
        sell_mode=SellModeEnum.online,
        title="Event",
        organizer_company_id=1,
        events=[event_a],
    )
    api.extract.return_value = json.dumps(base_event.dict(), default=str)
    api.parse.return_value = [base_event]
    event_service = ProviderService(repository=repository, api=api)

    events = await event_service.extract_events()

    assert events == [base_event]
    api.extract.assert_called_once_with()
    api.parse.assert_called_once()


async def test_retrieve_all_events_empty_response(mocker):
    repository = mocker.Mock(spec_set=BaseRepositoryProvider)
    api = mocker.Mock(spec_set=BaseApiProvider)
    api.extract.return_value = ""
    api.parse.return_value = []
    event_service = ProviderService(repository=repository, api=api)

    events = await event_service.extract_events()

    api.extract.assert_called_once_with()
    api.parse.assert_called_once_with("")
    assert events == []
