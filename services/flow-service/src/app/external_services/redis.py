import json
import logging
from typing import Any

import redis.asyncio as redis

from app.config.config import Config

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(
        self,
        redis_client: redis.Redis,
        config: Config
    ):
        self.redis_client = redis_client
        self.config = config

    async def get_products(self, flow_type: str) -> Any | None:
        """Получение продуктов из кэша"""
        key = f'products:{flow_type}'

        try:
            cached_products = await self.redis_client.get(key)
            if cached_products:
                return json.loads(cached_products)
        except redis.RedisError as e:
            logger.error(f'Redis GET Error, key: {key}, {e}')
        return None

    async def set_products(
        self,
        flow_type: str,
        products: list[dict[str, Any]]
    ) -> None:
        """Добавление продуктов в кэш"""
        key = f'products:{flow_type}'
        product_dumps = json.dumps(products)
        try:
            await self.redis_client.set(
                key,
                product_dumps,
                ex=self.config.redis.ttl
            )
        except redis.RedisError as e:
            logger.error(f'Redis SET Error: {e}')
