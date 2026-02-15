import json
from unittest.mock import AsyncMock

import pytest
import redis.asyncio as redis

from app.config.config import settings
from app.external_services.redis import RedisService


@pytest.mark.asyncio
async def test_redis_service_get_products_hit():
    mock_redis_client = AsyncMock(spec=redis.Redis)
    redis_service = RedisService(
        redis_client=mock_redis_client
    )
    flow_type = 'pioneer'
    key = f'products:{flow_type}'

    cached_data = [{
        'product_name': 'Product',
        'amount': 100, 'percentage': 5.0
    }]
    mock_redis_client.get = AsyncMock(return_value=json.dumps(cached_data))

    result = await redis_service.get_products(flow_type)

    mock_redis_client.get.assert_awaited_once_with(key)
    assert result == cached_data


@pytest.mark.asyncio
async def test_redis_service_get_products_miss():
    mock_redis_client = AsyncMock(spec=redis.Redis)
    redis_service = RedisService(
        redis_client=mock_redis_client)
    flow_type = 'repeater'
    key = f'products:{flow_type}'

    mock_redis_client.get = AsyncMock(return_value=None)

    result = await redis_service.get_products(flow_type)

    mock_redis_client.get.assert_awaited_once_with(key)
    assert result is None


@pytest.mark.asyncio
async def test_redis_service_get_products_error():
    mock_redis_client = AsyncMock(spec=redis.Redis)
    redis_service = RedisService(
        redis_client=mock_redis_client)
    flow_type = 'pioneer'
    key = f'products:{flow_type}'
    mock_redis_client.get = AsyncMock(side_effect=redis.RedisError())

    result = await redis_service.get_products(flow_type)

    mock_redis_client.get.assert_awaited_once_with(key)
    assert result is None


@pytest.mark.asyncio
async def test_redis_service_set_products_success():
    mock_redis_client = AsyncMock(spec=redis.Redis)
    redis_service = RedisService(
        redis_client=mock_redis_client)
    flow_type = 'pioneer'
    key = f'products:{flow_type}'
    products_to_cache = [{
        'product_name': 'Product', 'amount': 200, 'percentage': 7.0
    }]

    expected_redis_value = json.dumps(products_to_cache)
    mock_redis_client.set = AsyncMock()

    await redis_service.set_products(flow_type, products_to_cache)

    mock_redis_client.set.assert_awaited_once_with(
        key,
        expected_redis_value,
        ex=settings.REDIS_TTL
    )


@pytest.mark.asyncio
async def test_redis_service_set_products_error():
    mock_redis_client = AsyncMock(spec=redis.Redis)
    redis_service = RedisService(
        redis_client=mock_redis_client)
    flow_type = 'repeater'
    products_to_cache = [{
        'product_name': 'Product', 'amount': 150, 'percentage': 8.0
    }]
    mock_redis_client.set = AsyncMock(side_effect=redis.RedisError())

    try:
        await redis_service.set_products(flow_type, products_to_cache)
    except Exception as e:
        pytest.fail(f'exception: {e}')

    mock_redis_client.set.assert_awaited_once()
