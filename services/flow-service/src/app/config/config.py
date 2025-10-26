from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class RetriesConfig(BaseModel):
    max_attempts: int = Field(..., alias='max_attempts')
    delay: int = Field(..., alias='delay')


class DataServiceConfig(BaseModel):
    base_url: str
    timeout: int
    retries: RetriesConfig


class Config(BaseModel):
    data_service: DataServiceConfig

    @classmethod
    def from_yaml(cls, file_path: Path | str) -> 'Config':
        config_raw = yaml.safe_load(Path(file_path).read_text(encoding='utf-8'))
        return cls.model_validate(config_raw)
