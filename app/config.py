from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseModel):
    class_name: str
    module_path: str
    config: dict[str, str] = {}  # configuration to instantiate the provider


class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int

    model_config = SettingsConfigDict(frozen=True)
