import httpx
import pytest
from httpx import HTTPStatusError
from starlette import status

from app.application.use_cases.update_events import (
    ResultStatus,
    ResultUpdateProvider,
    UpdateEventsUseCase,
)
from app.domain.entities.provider_a.provider_a import ProviderABaseEvent, SellModeEnum
from app.infrastructure.api.external_providers.base import BaseApiProvider
from app.infrastructure.repository.base import BaseRepositoryProvider


@pytest.fixture
def use_case(mocker):
    use_case = UpdateEventsUseCase(
        api=mocker.Mock(spec_set=BaseApiProvider),
        repository=mocker.Mock(spec_set=BaseRepositoryProvider),
    )
    use_case._event_service = mocker.AsyncMock()
    return use_case


async def test_execute_no_online_events(use_case):
    use_case._event_service.extract_events.return_value = [
        ProviderABaseEvent(
            sell_mode=SellModeEnum.offline,
            title="Event 1",
            organizer_company_id=1,
            events=[],
            base_event_id=1,
        ),
    ]
    use_case._event_service.store_events.return_value = ResultUpdateProvider(status=ResultStatus.OK)
    result = await use_case.execute()

    assert result.status == ResultStatus.OK
    assert result.error_description is None
    use_case._event_service.extract_events.assert_called_with()
    use_case._event_service.store_events.assert_called_with([])


async def test_execute_parsing_error(use_case):
    use_case._event_service.extract_events.side_effect = ValueError

    result = await use_case.execute()

    assert result.status == ResultStatus.ERROR
    assert result.error_description == "Error updating events"
    use_case._event_service.extract_events.assert_called_with()
    use_case._event_service.store_events.assert_not_called()


async def test_execute_connection_error(use_case, mocker, caplog):
    response = httpx.Response(status_code=status.HTTP_400_BAD_REQUEST)
    status_error = HTTPStatusError(request=mocker.Mock(), response=response, message="Connection error")
    use_case._event_service.extract_events.side_effect = status_error

    result = await use_case.execute()

    assert result.status == ResultStatus.ERROR
    use_case._event_service.extract_events.assert_called_with()
    use_case._event_service.store_events.assert_not_called()
    assert "Error updating events: Connection error" in caplog.text


async def test_execute_unexpected_error(use_case, caplog):
    use_case._event_service.extract_events.side_effect = Exception("Unexpected error")

    result = await use_case.execute()

    assert result.status == ResultStatus.ERROR
    use_case._event_service.extract_events.assert_called_with()
    use_case._event_service.store_events.assert_not_called()
    assert "Error updating events: Unexpected error" in caplog.text


async def test_execute_happy_path(use_case):
    use_case._event_service.extract_events.return_value = [
        ProviderABaseEvent(
            sell_mode=SellModeEnum.online,
            title="Event 1",
            organizer_company_id=1,
            events=[],
            base_event_id=1,
        ),
        ProviderABaseEvent(
            sell_mode=SellModeEnum.offline,
            title="Event 2",
            organizer_company_id=2,
            events=[],
            base_event_id=2,
        ),
        ProviderABaseEvent(
            sell_mode=SellModeEnum.online,
            title="Event 3",
            organizer_company_id=3,
            events=[],
            base_event_id=3,
        ),
    ]

    result = await use_case.execute()

    assert result.status == ResultStatus.OK
    assert result.error_description is None
    expected = [
        ProviderABaseEvent(
            base_event_id=1,
            sell_mode=SellModeEnum.online,
            title="Event 1",
            organizer_company_id=1,
            events=[],
        ),
        ProviderABaseEvent(
            base_event_id=3,
            sell_mode=SellModeEnum.online,
            title="Event 3",
            organizer_company_id=3,
            events=[],
        ),
    ]
    use_case._event_service.store_events.assert_called_once_with(expected)
