from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.external_services.redis import RedisService
from app.logic.flow_service import FlowService


@pytest.fixture
def flow_service_fixture():
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)
    mock_redis_service = AsyncMock(spec=RedisService)

    service = FlowService(
        client=mock_http_client,
        redis_service=mock_redis_service
    )
    return service, mock_http_client, mock_redis_service


@pytest.mark.asyncio
async def test_check_client_type_repeater(flow_service_fixture):
    flow_service, mock_client, _ = flow_service_fixture
    mock_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_client.get.return_value = mock_response

    result = await flow_service.check_client_type('79123456789')

    assert result == 'repeater'
    mock_client.get.assert_awaited_once_with('/user-data?phone=79123456789')


@pytest.mark.asyncio
async def test_check_client_type_pioneer(flow_service_fixture):
    flow_service, mock_client, _ = flow_service_fixture
    mock_response = MagicMock(spec=httpx.Response, status_code=404)
    mock_client.get.return_value = mock_response

    result = await flow_service.check_client_type('79123456789')

    assert result == 'pioneer'


@pytest.mark.asyncio
async def test_check_client_type_raises_exception(flow_service_fixture):
    flow_service, mock_client, _ = flow_service_fixture
    mock_response = MagicMock(spec=httpx.Response, status_code=500)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        'StatusError',
        request=MagicMock(),
        response=mock_response
    )
    mock_client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        await flow_service.check_client_type('79123456789')


@pytest.mark.asyncio
async def test_flow_selection_repeater_when_cache_miss(flow_service_fixture):
    flow_service, mock_client, mock_redis = flow_service_fixture
    phone = '79123456789'
    expected_products = [{'product_name': 'Product'}]

    mock_redis.get_products.return_value = None

    user_data_response = MagicMock(spec=httpx.Response, status_code=200)
    products_response = MagicMock(spec=httpx.Response, status_code=200)
    products_response.json.return_value = expected_products
    mock_client.get.side_effect = [user_data_response, products_response]

    result = await flow_service.flow_type_selection(phone)

    assert result['flow_type'] == 'repeater'
    assert result['available_products'] == expected_products

    mock_redis.get_products.assert_awaited_once_with('repeater')
    assert mock_client.get.call_count == 2
    mock_client.get.assert_any_await('/user-data?phone=79123456789')
    mock_client.get.assert_any_await('/api/products?flow_type=repeater')
    mock_redis.set_products.assert_awaited_once_with(
        'repeater', expected_products)


@pytest.mark.asyncio
async def test_flow_selection_pioneer_when_cache_hit(flow_service_fixture):
    flow_service, mock_client, mock_redis = flow_service_fixture
    phone = '79123456789'
    cached_products = [{'product_name': 'Product'}]

    mock_redis.get_products.return_value = cached_products

    user_data_response = MagicMock(spec=httpx.Response, status_code=404)
    mock_client.get.return_value = user_data_response

    result = await flow_service.flow_type_selection(phone)

    assert result['flow_type'] == 'pioneer'
    assert result['available_products'] == cached_products

    mock_redis.get_products.assert_awaited_once_with('pioneer')
    mock_client.get.assert_awaited_once_with('/user-data?phone=79123456789')
    mock_redis.set_products.assert_not_awaited()


@pytest.mark.asyncio
async def test_flow_selection_when_user_data_fails_after_retries(flow_service_fixture):
    flow_service, mock_client, mock_redis = flow_service_fixture

    mock_client.get.side_effect = httpx.TimeoutException('Error')

    with pytest.raises(httpx.TimeoutException):
        await flow_service.flow_type_selection('79123456789')

    assert mock_client.get.call_count == 3
    mock_redis.get_products.assert_not_awaited()


@pytest.mark.asyncio
async def test_flow_selection_when_products_service_fails(flow_service_fixture):
    flow_service, mock_client, mock_redis = flow_service_fixture

    mock_redis.get_products.return_value = None

    user_data_response = MagicMock(spec=httpx.Response, status_code=200)
    products_failure = httpx.HTTPStatusError(
        'StatusError',
        request=MagicMock(),
        response=MagicMock()
    )
    mock_client.get.side_effect = [user_data_response, products_failure]

    with pytest.raises(httpx.HTTPStatusError):
        await flow_service.flow_type_selection('79123456789')

    mock_redis.get_products.assert_awaited_once_with('repeater')
    assert mock_client.get.call_count == 2
