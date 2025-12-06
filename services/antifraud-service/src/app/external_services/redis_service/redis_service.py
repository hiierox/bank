import logging
from datetime import timedelta

from redis.asyncio.client import Redis
from redis.exceptions import RedisError

from app.core.constants import P1_CHECK_PERIOD_HOURS
from app.core.exceptions import IntegrationError

logger = logging.getLogger(__name__)


class RedisService:
    """Сервис для работы c Redis"""

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.ttl = timedelta(hours=P1_CHECK_PERIOD_HOURS)

    def _get_key(self, phone: str) -> str:
        """Формирует ключ для счетчика заявок по номеру телефона."""
        return f'application_count:{phone}'

    async def get_application_count(self, phone: str) -> int:
        """
        Возвращает количество заявок, поданных c номера за последние 24 часа.
        Возвращает 0, если ключ не существует.
        """
        key = self._get_key(phone)
        try:
            count_str = await self.redis_client.get(key)

            if count_str is None:
                return 0

            return int(count_str)

        except RedisError as e:
            logger.error(f'Redis ошибка для ключа {key}: {e}')
            raise IntegrationError('He удалось получить данные из Redis') from e
        except ValueError as e:
            logger.error(f'Неверный формат данных из Redis по ключу {key}: {e}')
            raise IntegrationError('Неверный формат данных в Redis') from e

    async def increment_application_count(self, phone: str) -> None:
        """
        Инкрементирует счетчик заявок и устанавливает TTL
        """
        key = self._get_key(phone)
        try:
            new_count = await self.redis_client.incr(key)

            if new_count == 1:
                await self.redis_client.expire(key, self.ttl)

            logger.info(
                f'Инкрементировано счетчик для {phone}. Текущее значение: {new_count}'
                )

        except RedisError as e:
            logger.error(f'Ошибка при INCR/EXPIRE по ключу {key}: {e}')
            raise IntegrationError('Ошибка при INCR/EXPIRE') from e
