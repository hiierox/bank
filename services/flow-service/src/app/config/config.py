from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATA_SERVICE_MAX_ATTEMPTS: int = 2
    DATA_SERVICE_DELAY: int = 1
    DATA_SERVICE_BASE_URL: str = 'default_base_url'
    DATA_SERVICE_TIMEOUT: int = 5
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_TTL: int = 60

settings = Settings()
