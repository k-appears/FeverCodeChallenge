import logging
from typing import Sequence

from fastapi_cache.decorator import cache
from redis.exceptions import RedisError

from app.domain.entities.event import AbstractEvent
from app.domain.entities.provider_a.provider_a import ProviderABaseEvent
from app.infrastructure.database import RedisBase
from app.infrastructure.repository.base import BaseRepositoryProvider
from app.infrastructure.repository.entities import DatabaseError, FilterQuery

ROOT_KEY = "event"
log = logging.getLogger(__name__)


class ProviderA(BaseRepositoryProvider):
    def __init__(self, redis: RedisBase):
        self._redis = redis

    async def add_or_update_events(self, base_events: Sequence[AbstractEvent]) -> None:
        try:
            await self._redis_store(base_events)
        except (ValueError, RedisError, OSError) as g_e:
            log.error(f"Error storing in Redis: {g_e}", exc_info=True)
            raise DatabaseError(g_e)
        except Exception as e:
            log.error(f"Unexpected error storing in Redis: {e}", exc_info=True)
            raise

    async def get_all(self, filter_query: FilterQuery) -> list[AbstractEvent]:
        # Find event IDs that start after event_start
        start_timestamp = filter_query.starts_at.timestamp()
        end_timestamp = filter_query.ends_at.timestamp()
        try:
            pipeline = self._redis.pipeline()
            # Get from sorted Set events start after event_start and events end before event_end
            pipeline.zrangebyscore("event_start", start_timestamp, "+inf")
            pipeline.zrangebyscore("event_end", "-inf", end_timestamp)
            [start_event_ids, end_event_ids] = await pipeline.execute()

            # Computational Intersection instead of ZINTERSTORE to avoid blocking the Redis server
            event_ids = set(start_event_ids) & set(end_event_ids)

            base_events = {}

            for event_id in event_ids:
                base_ids = await self._get_base_ids(event_id.decode())
                base_event_data_list = await self._get_base_event_data(base_ids)
                for base_event_data in base_event_data_list:
                    base_event = ProviderABaseEvent.model_validate_json(base_event_data)
                    base_events[base_event.base_event_id] = base_event

            return list(base_events.values())
        except (ValueError, RedisError, OSError) as g_e:
            log.error(f"Error getting events in Redis: {g_e}", exc_info=True)
            raise DatabaseError(g_e)
        except Exception as e:
            log.error(f"Unexpected error getting events in Redis: {e}", exc_info=True)
            raise

    @cache()
    async def _get_base_ids(self, event_id: str) -> set[str]:
        return {
            base_id.decode().split(":")[1]
            async for base_id in self._redis.scan_iter(f"{ROOT_KEY}:*:{event_id}")
            if base_id
        }

    @cache()
    async def _get_base_event_data(self, base_ids: set[str]) -> list[bytes]:
        return [
            base_event_data
            for base_id in base_ids
            if (base_event_data := await self._redis.get(f"{ROOT_KEY}:{base_id}"))
        ]

    async def _redis_store(self, base_events: Sequence[AbstractEvent]) -> None:
        # Improved performance with indexes for event_start and event_end instead of adding a JSON document to an index
        pipeline = self._redis.pipeline()  # transactional pipeline
        for base_event in base_events:
            if isinstance(base_event, ProviderABaseEvent):
                pipeline.set(f"{ROOT_KEY}:{base_event.base_event_id}", base_event.model_dump_json())
                for event in base_event.events:
                    pipeline.zadd("event_start", {str(event.event_id): event.event_start_date.timestamp()})
                    pipeline.zadd("event_end", {str(event.event_id): event.event_end_date.timestamp()})
                    pipeline.set(f"{ROOT_KEY}:{base_event.base_event_id}:{event.event_id}", base_event.base_event_id)
        await pipeline.execute()
