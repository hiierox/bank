import json
import logging
from typing import Any

import redis.asyncio as redis
from opentelemetry.semconv._incubating.attributes.db_attributes import (
    DB_OPERATION,
    DB_STATEMENT,
    DB_SYSTEM,
)

from app.config.config import settings
from app.external_services.monitoring.tracing import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer()

class RedisService:
    def __init__(
        self,
        redis_client: redis.Redis,
    ):
        self.redis_client = redis_client

    async def get_products(self, flow_type: str) -> Any | None:
        """Получение продуктов из кэша"""
        key = f'products:{flow_type}'
        with tracer.start_as_current_span('redis.get') as span:
            span.set_attribute(DB_SYSTEM, 'redis')
            span.set_attribute(DB_OPERATION, 'get')
            span.set_attribute(DB_STATEMENT, f'GET {key}')
            try:
                cached_products = await self.redis_client.get(key)
                if cached_products:
                    span.set_attribute('db.redis.hit', True)
                    return json.loads(cached_products)
                else:  # noqa: RET505
                    span.set_attribute('db.redis.hit', False)
            except redis.RedisError as e:
                span.record_exception(e)
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
        with tracer.start_as_current_span('redis.set') as span:
            span.set_attribute(DB_SYSTEM, 'redis')
            span.set_attribute(DB_OPERATION, 'set')
            span.set_attribute(DB_STATEMENT, f'SET {key} EX {settings.REDIS_TTL}')

            try:
                await self.redis_client.set(
                    key,
                    product_dumps,
                    ex=settings.REDIS_TTL
                )
            except redis.RedisError as e:
                span.record_exception(e)
                logger.error(f'Redis SET Error: {e}')
