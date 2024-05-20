import os
from pathlib import Path

import fastapi_cache
import pytest
from fastapi_cache.backends.inmemory import InMemoryBackend
from testcontainers.compose import DockerCompose

from app.adapters.dependencies import ProviderConfig, ProvidersConfig


@pytest.fixture()
def docker_dependencies():
    doker_compose_file = Path(__file__).parent.parent / "docker"

    with DockerCompose(doker_compose_file) as compose:
        host, port = compose.get_service_host_and_port("mock-event-service")
        endpoint = f"http://{host}:{port}"  # no qa E231 missing whitespace after ':'
        compose.wait_for(endpoint)

        os.environ["ENV"] = "localhost"
        yield compose
        os.environ.pop("ENV")


@pytest.fixture
def redis_mock(mocker):
    redis_mock = mocker.MagicMock()
    pipeline = mocker.AsyncMock()
    pipeline.zadd = mocker.Mock()
    pipeline.set = mocker.Mock()
    pipeline.zrangebyscore = mocker.Mock(return_value=[])
    redis_mock.pipeline.return_value = pipeline
    return redis_mock


@pytest.fixture
def mock_providers_config():
    return ProvidersConfig(
        external_providers=[
            ProviderConfig(
                api_module_path="api_module",
                repository_module_path="repository_module",
                class_name="TestClass",
                config={"param1": "value1", "param2": "value2"},
            ),
        ],
    )


@pytest.fixture
def mock_cache():
    fastapi_cache.FastAPICache.init(InMemoryBackend())
    yield
    fastapi_cache.FastAPICache.reset()
