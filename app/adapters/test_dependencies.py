from unittest.mock import mock_open

import pytest
import yaml
from pydantic import ValidationError

from app.adapters.dependencies import get_providers_config


@pytest.fixture
def clear_cache_mock():
    get_providers_config.cache_clear()
    yield
    get_providers_config.cache_clear()


def test_get_providers_config_no_valid_provider(clear_cache_mock, mocker):
    config_data = {
        "external_providers": [
            {"repository_module_path": "path1", "class_name": "class1", "config": {}},
        ],
    }
    mocker.patch("builtins.open", mock_open(read_data=yaml.dump(config_data)))
    with pytest.raises(ValidationError) as exc_info:
        get_providers_config()
    assert exc_info.value.errors() == [
        {
            "input": {"class_name": "class1", "config": {}, "repository_module_path": "path1"},
            "loc": ("external_providers", 0, "api_module_path"),
            "msg": "Field required",
            "type": "missing",
            "url": "https://errors.pydantic.dev/2.7/v/missing",
        },
    ]


def test_get_providers_config_no_config_data(clear_cache_mock, mocker):
    get_providers_config.cache_clear()
    mocker.patch("builtins.open", mock_open(read_data=""))
    with pytest.raises(ValueError) as exc_info:
        get_providers_config()
    assert "Input should be a valid dictionary or instance of ProvidersConfig" in str(exc_info.value)


def test_get_providers_config_happy_path(clear_cache_mock, mocker):
    config_data = {
        "external_providers": [
            {"class_name": "class1", "repository_module_path": "path1", "api_module_path": "path1_1", "config": {}},
            {
                "class_name": "class2",
                "repository_module_path": "path2",
                "api_module_path": "path2_1",
                "config": {"key1": "value1"},
            },
        ],
    }
    mocker.patch("builtins.open", mock_open(read_data=yaml.dump(config_data)))
    providers = get_providers_config()
    assert providers.dict() == config_data
