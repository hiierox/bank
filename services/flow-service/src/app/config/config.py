from pathlib import Path

import yaml
from pydantic import BaseModel


class RetriesConfig(BaseModel):
    max_attempts: int
    delay: int


class DataServiceConfig(BaseModel):
    base_url: str
    timeout: int
    retries: RetriesConfig


class RedisConfig(BaseModel):
    host: str
    port: int
    ttl: int


class Config(BaseModel):
    data_service: DataServiceConfig
    redis: RedisConfig

    @classmethod
    def from_yaml(cls, file_path: Path | str) -> 'Config':
        config_raw = yaml.safe_load(Path(file_path).read_text(encoding='utf-8'))
        return cls.model_validate(config_raw)
