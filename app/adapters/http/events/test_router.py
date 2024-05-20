from datetime import datetime

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import main
from app.adapters.http.events.router import get_events
from app.application.dtos.events import EventDTO, EventsDTO, ResponseEventDTO
from app.application.use_cases.request_events import RequestEventsUseCase
from app.infrastructure.repository.entities import FilterQuery


@pytest.mark.integration
async def test_get_events_error_starts_after_end():
    client = TestClient(main.app)
    response = client.get("/search", params={"starts_at": "2022-01-02T00:00:00", "ends_at": "2022-01-01T00:00:00"})
    assert response.status_code == status.HTTP_200_OK
    event = ResponseEventDTO.model_validate(response.json())
    assert event.data is None
    assert event.error.code == str(status.HTTP_400_BAD_REQUEST)
    assert event.error.message == "starts_at must be less than ends_at"


async def test_get_events_happy_path(mock_providers_config, mocker):
    mocker.patch("importlib.import_module", return_value=mocker.Mock())
    response_mock = mocker.Mock(spec_set=EventDTO)
    execute_mock = mocker.AsyncMock(return_value=ResponseEventDTO(data=EventsDTO(events=[response_mock])))
    mocker.patch.object(RequestEventsUseCase, "execute", execute_mock)

    starts_at = datetime(2021, 1, 1, tzinfo=datetime.now().astimezone().tzinfo)
    ends_at = datetime(2022, 1, 2, tzinfo=datetime.now().astimezone().tzinfo)
    result = await get_events(
        starts_at=starts_at,
        ends_at=ends_at,
        redis=mocker.AsyncMock(),
        providers_config=mock_providers_config,
    )

    assert result.error is None
    assert len(result.data.events) == 1
    assert result.data.events == [response_mock]
    execute_mock.assert_awaited_with(FilterQuery(starts_at=starts_at, ends_at=ends_at))


async def test_update_events_no_providers_config(mock_providers_config, mocker):
    mocker.patch("importlib.import_module", side_effect=AttributeError("Error class 'TestClass' not found"))

    with pytest.raises(ValueError) as exc_info:
        await get_events(
            starts_at=datetime(2021, 1, 1),
            ends_at=datetime(2022, 1, 2),
            redis=mocker.Mock(),
            providers_config=mock_providers_config,
        )

    assert str(exc_info.value) == "Class not found  TestClass in module repository_module"
