from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настраивает БД из переменных окружения
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATABASE_URL: str = 'postgresql+asyncpg://user:pass@host:port/db'
    KAFKA_BOOTSTRAP_SERVERS: str = 'localhost:9092'
    KAFKA_TOPIC: str = 'default_topic'
    KAFKA_GROUP_ID: str = 'default_group_id'

settings = Settings()
