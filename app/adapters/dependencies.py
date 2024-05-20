import logging
import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

from app.config import Settings

CONFIG_PATH = Path(__file__).parent.parent / "infrastructure" / "config"

log = logging.getLogger(__name__)


class ProviderConfig(BaseModel):
    class_name: str
    api_module_path: str
    repository_module_path: str
    config: dict[str, str]


class ProvidersConfig(BaseModel):
    external_providers: list[ProviderConfig]


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=CONFIG_PATH / os.getenv("ENV", "localhost") / ".env")


@lru_cache
def get_providers_config() -> ProvidersConfig:
    with open(CONFIG_PATH / os.getenv("ENV", "localhost") / "config.yaml", "r") as f:
        config_data = yaml.safe_load(f)
        log.info(f"Configuration loaded successfully: {config_data}")
    return ProvidersConfig.model_validate(config_data)
