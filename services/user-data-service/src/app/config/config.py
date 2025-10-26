from pathlib import Path

import yaml
from pydantic import BaseModel


class KafkaConfig(BaseModel):
    """Модель конфигурации для Kafka."""
    bootstrap_servers: str
    topic: str
    group_id: str


class Config(BaseModel):
    """Основная модель конфигурации приложения."""
    kafka: KafkaConfig

    @classmethod
    def from_yaml(cls, file_path: Path | str) -> 'Config':
        """
        Загружает и валидирует конфигурацию из YAML-файла
        """
        config_raw = yaml.safe_load(Path(file_path).read_text(encoding='utf-8'))
        return cls.model_validate(config_raw)
