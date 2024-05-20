import pytest
from redis import RedisError

from app.application.dtos.events import EventsDTO
from app.application.use_cases.request_events import RequestEventsUseCase
from app.infrastructure.repository.provider_a import ProviderA


@pytest.fixture
async def repository_use_case(redis_mock):
    repository = ProviderA(redis=redis_mock)
    use_case = RequestEventsUseCase(repository)
    return use_case


async def test_execute_failed_redis_error(redis_mock, repository_use_case, mocker):
    redis_mock.pipeline.side_effect = RedisError("Error retrieving events")
    filter_query = mocker.Mock()
    result = await repository_use_case.execute(filter_query)
    assert result.data is None
    assert result.error.message == "Error retrieving events"


async def test_execute_failed_unexpected_exception(redis_mock, repository_use_case, mocker):
    redis_mock.pipeline.side_effect = KeyError("Error retrieving events")
    filter_query = mocker.Mock()
    result = await repository_use_case.execute(filter_query)
    assert result.data is None
    assert result.error.message == "'Error retrieving events'"


async def test_execute_empty_response(redis_mock, repository_use_case, mocker):
    redis_mock.pipeline().execute.return_value = [[], []]
    filter_query = mocker.Mock()
    result = await repository_use_case.execute(filter_query)
    assert result.data == EventsDTO(events=[])
    assert result.error is None
    redis_mock.pipeline().execute.assert_called_once()
    redis_mock.scan_iter.assert_not_called()
    redis_mock.get.assert_not_called()
