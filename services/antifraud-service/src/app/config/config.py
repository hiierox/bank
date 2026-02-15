from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATA_SERVICE_BASE_URL: str = 'default_base_url'
    DATA_SERVICE_TIMEOUT: int = 5
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

settings = Settings()
