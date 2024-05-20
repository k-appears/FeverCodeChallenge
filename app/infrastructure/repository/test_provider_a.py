import asyncio
from datetime import datetime

import pytest
from redis.exceptions import RedisError

from app.conftest import redis_mock
from app.domain.entities.provider_a.provider_a import (
    ProviderABaseEvent,
    ProviderAEvent,
    SellModeEnum,
)
from app.infrastructure.repository.entities import DatabaseError, FilterQuery
from app.infrastructure.repository.provider_a import ProviderA

event_1 = ProviderAEvent(
    event_id=11,
    event_start_date=datetime(2020, 1, 1),
    event_end_date=datetime(2020, 1, 2),
    sell_from=datetime(2020, 1, 1),
    sell_to=datetime(2020, 1, 2),
    sold_out=False,
    zones=[],
)
event_2 = ProviderAEvent(
    event_id=12,
    event_start_date=datetime(2020, 1, 1),
    event_end_date=datetime(2020, 1, 2),
    sell_from=datetime(2020, 1, 1),
    sell_to=datetime(2020, 1, 2),
    sold_out=False,
    zones=[],
)
base_event_1 = ProviderABaseEvent(
    base_event_id=1,
    sell_mode=SellModeEnum.online,
    title="Event 1",
    organizer_company_id=1,
    events=[event_1, event_2],
)
event_3 = ProviderAEvent(
    event_id=23,
    event_start_date=datetime(2020, 1, 1),
    event_end_date=datetime(2020, 1, 2),
    sell_from=datetime(2020, 1, 1),
    sell_to=datetime(2020, 1, 2),
    sold_out=False,
    zones=[],
)
base_event_2 = ProviderABaseEvent(
    base_event_id=2,
    sell_mode=SellModeEnum.online,
    title="Event 2",
    organizer_company_id=2,
    events=[event_1, event_3],
)


@pytest.fixture
def base_events():
    return [base_event_1, base_event_2]


async def test_store_events_happy_path(base_events, redis_mock, mocker):
    repository = ProviderA(redis_mock)
    await repository.add_or_update_events(base_events)

    pipeline_mock = redis_mock.pipeline()

    assert pipeline_mock.zadd.call_count == 8
    pipeline_mock.zadd.assert_any_call("event_end", {"11": event_1.event_end_date.timestamp()})
    pipeline_mock.zadd.assert_any_call("event_end", {"12": event_2.event_end_date.timestamp()})
    pipeline_mock.zadd.assert_any_call("event_end", {"23": event_3.event_end_date.timestamp()})
    pipeline_mock.zadd.assert_any_call("event_start", {"11": event_1.event_start_date.timestamp()})
    pipeline_mock.zadd.assert_any_call("event_start", {"12": event_2.event_start_date.timestamp()})
    pipeline_mock.zadd.assert_any_call("event_start", {"23": event_3.event_start_date.timestamp()})
    assert pipeline_mock.set.call_count == 6
    pipeline_mock.set.assert_any_call("event:1", mocker.ANY)
    pipeline_mock.set.assert_any_call("event:2", mocker.ANY)
    pipeline_mock.set.assert_any_call("event:1:11", mocker.ANY)
    pipeline_mock.set.assert_any_call("event:1:12", mocker.ANY)
    pipeline_mock.set.assert_any_call("event:2:23", mocker.ANY)
    pipeline_mock.set.assert_any_call("event:2:11", mocker.ANY)


async def test_retrieve_events_happy_path(redis_mock, mock_cache, mocker):
    pipeline_mock = redis_mock.pipeline()
    pipeline_mock.execute.side_effect = [[[b"11", b"12"], [b"11"]]]
    redis_mock.get = mocker.AsyncMock(side_effect=[base_event_1.model_dump_json(), base_event_2.model_dump_json()])
    mock_aiter = mocker.MagicMock()
    mock_aiter.__aiter__.return_value = [b"event:1:11", b"event:2:11"]
    redis_mock.scan_iter.side_effect = mocker.MagicMock(return_value=mock_aiter)
    gather_mock = mocker.AsyncMock(return_value=[base_event_1.model_dump_json(), base_event_2.model_dump_json()])
    mocker.patch.object(asyncio, "gather", gather_mock)

    repository = ProviderA(redis_mock)
    filter_query = FilterQuery(starts_at=datetime(2020, 1, 1), ends_at=datetime(2020, 1, 2))
    result = await repository.get_all(filter_query)

    assert len(result) == 2
    assert base_event_2 in result
    assert base_event_1 in result
    redis_mock.scan_iter.assert_called_once_with("event:*:11")
    assert redis_mock.get.call_count == 2
    redis_mock.get.assert_any_call("event:1")
    redis_mock.get.assert_any_call("event:2")


async def test_get_all_events_error(redis_mock):
    redis_mock.pipeline.side_effect = RedisError("Generic Redis error")
    repository = ProviderA(redis_mock)
    filter_query = FilterQuery(starts_at=datetime(2020, 1, 1), ends_at=datetime(2020, 1, 2))
    with pytest.raises(DatabaseError) as de:
        await repository.get_all(filter_query)
    assert "Generic Redis error" in str(de)


async def test_store_events_error(redis_mock, mocker):
    redis_mock.pipeline.side_effect = RedisError("Generic Redis storing in error")
    repository = ProviderA(redis_mock)
    with pytest.raises(DatabaseError) as de:
        await repository.add_or_update_events(mocker.Mock())
    assert "Generic Redis storing in error" in str(de)
