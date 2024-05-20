import pytest

from app.adapters.update_events import update_events
from app.application.use_cases.update_events import (
    ResultStatus,
    ResultUpdateProvider,
    UpdateEventsUseCase,
)
from app.conftest import mock_providers_config


async def test_update_events_happy_path(mock_providers_config, mocker):
    mocker.patch("importlib.import_module", return_value=mocker.Mock())
    execute_mock = mocker.AsyncMock(return_value=ResultUpdateProvider(status=ResultStatus.OK))
    mocker.patch.object(UpdateEventsUseCase, "execute", execute_mock)

    result = await update_events(redis=mocker.Mock(), providers_config=mock_providers_config)

    assert len(result) == 1
    assert result[0].status == ResultStatus.OK
    execute_mock.assert_awaited_with()


async def test_update_events_no_providers_config(mock_providers_config, mocker):
    mocker.patch("importlib.import_module", side_effect=AttributeError("Error class 'TestClass' not found"))

    with pytest.raises(ValueError) as exc_info:
        await update_events(redis=mocker.AsyncMock(), providers_config=mock_providers_config)

    assert str(exc_info.value) == "Class not found  TestClass in module repository_module"
