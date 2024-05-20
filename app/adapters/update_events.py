import importlib
import logging

from fastapi import Depends

from app.adapters.dependencies import (
    ProviderConfig,
    ProvidersConfig,
    get_providers_config,
)
from app.application.use_cases.update_events import (
    ResultUpdateProvider,
    UpdateEventsUseCase,
)
from app.infrastructure.database import RedisBase, create_redis_client

log = logging.getLogger(__name__)


def _create_use_case(provider: ProviderConfig, redis: RedisBase) -> UpdateEventsUseCase:
    try:
        api_module = importlib.import_module(provider.api_module_path)
        repository_module = importlib.import_module(provider.repository_module_path)
        return UpdateEventsUseCase(
            getattr(api_module, provider.class_name)(**provider.config),
            getattr(repository_module, provider.class_name)(redis),
        )
    except Exception as e:
        log.error(f"Invalid configuration: {e}", exc_info=True)
        raise ValueError(f"Class not found  {provider.class_name} in module {provider.repository_module_path}")


async def update_events(
    redis: RedisBase = Depends(create_redis_client),
    providers_config: ProvidersConfig = Depends(get_providers_config),
) -> list[ResultUpdateProvider]:
    result = []
    for provider in providers_config.external_providers:
        use_case = _create_use_case(provider, redis)
        result.append(await use_case.execute())
    return result
