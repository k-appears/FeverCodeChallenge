import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from app.adapters.dependencies import get_providers_config, get_settings
from app.adapters.http.events.router import event_router
from app.adapters.update_events import update_events
from app.infrastructure.database import create_redis_client, get_or_create_redis_pool

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    providers = get_providers_config()
    settings = get_settings()
    pool = get_or_create_redis_pool(settings=settings)  # Future Work shared pool with several Redis instances
    client = await create_redis_client(pool)
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")
    # Future Work create a locking job
    # update_job = await scheduler_pool.enqueue_job('update_events', client, providers, _job_id='update_events')
    # result = await update_job.result()

    result = await update_events(client, providers)
    await client.close()
    log.info(f"Update events for providers: {result}")
    yield
    await pool.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(event_router, tags=["events"])


@app.get("/", include_in_schema=False)
async def read_root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error(f"Internal Server Error, request:{request}, exception: {exc}", exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})
