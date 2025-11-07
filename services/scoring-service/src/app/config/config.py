from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATA_SERVICE_BASE_URL: str = 'http://localhost:8002'
    DATA_SERVICE_TIMEOUT: int = 5
    DATA_SERVICE_RETRIES_MAX_ATTEMPTS: int = 2
    DATA_SERVICE_RETRIES_DELAY: int = 1
    KAFKA_BOOTSTRAP_SERVERS: str = 'localhost:9092'
    KAFKA_TOPIC: str = 'default_topic'
    KAFKA_TIMEOUT_MS: int = 100

settings = Settings()
