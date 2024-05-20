from functools import lru_cache
from typing import TYPE_CHECKING, Never

import redis
from fastapi import Depends
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from app.adapters.dependencies import get_settings
from app.config import Settings

if TYPE_CHECKING:  # https://github.com/python/typeshed/issues/8242#issuecomment-1224316223
    RedisBase = Redis[bytes]
    ConnectionPoolBase = ConnectionPool[Never]  # Used Never in official documentation
else:
    RedisBase = Redis
    ConnectionPoolBase = ConnectionPool


@lru_cache
def get_or_create_redis_pool(settings: Settings = Depends(get_settings)) -> ConnectionPoolBase:
    # Future work change pool to ARQ when using jobs
    protocol = "redis"
    return ConnectionPool.from_url(f"{protocol}://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}")


async def create_redis_client(pool: ConnectionPoolBase = Depends(get_or_create_redis_pool)) -> RedisBase:
    redis_client = redis.asyncio.Redis(connection_pool=pool)
    return redis_client
