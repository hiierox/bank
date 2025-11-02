import json
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import redis.asyncio as redis
from fastapi.testclient import TestClient

from app.dependencies import get_config, get_http_client, get_redis_service
from app.external_services.redis import RedisService
from app.service import app


@pytest.fixture
def client_with_mocked_deps():
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)
    mock_redis_client = AsyncMock(spec=redis.Redis)

    app.dependency_overrides[get_http_client] = lambda: mock_http_client
    app.dependency_overrides[get_redis_service] = lambda: RedisService(
        mock_redis_client,
        get_config()
    )
    test_client = TestClient(app)

    yield test_client, mock_http_client, mock_redis_client

    app.dependency_overrides.clear()


def test_pioneer_flow_api_redis_miss(client_with_mocked_deps):
    test_client, mock_http_client, mock_redis_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}
    expected_products = [
        {'product_name': 'Product', 'amount': 100, 'percentage': 10.5}]

    mock_redis_client.get = AsyncMock(return_value=None)
    mock_redis_client.set = AsyncMock()
    mock_is_user_in_db_respone = MagicMock(spec=httpx.Response)
    mock_is_user_in_db_respone.status_code = 404

    products_response = MagicMock(spec=httpx.Response)
    products_response.json.return_value = expected_products
    products_response.status_code = 200

    mock_http_client.get.side_effect = [mock_is_user_in_db_respone, products_response]

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'pioneer'
    assert response_data['available_products'] == expected_products
    mock_redis_client.get.assert_awaited_once_with('products:pioneer')
    mock_http_client.get.assert_any_await('/user-data?phone=79123456789')
    mock_http_client.get.assert_any_await('/api/products?flow_type=pioneer')
    mock_redis_client.set.assert_awaited_once()


def test_repeater_flow_api_redis_miss(client_with_mocked_deps):
    test_client, mock_http_client, mock_redis_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}
    expected_products = [{'product_name': 'Product', 'amount': 100, 'percentage': 10.5}]

    mock_redis_client.set = AsyncMock()
    mock_redis_client.get = AsyncMock(return_value=None)

    mock_is_user_in_db_respone = MagicMock(spec=httpx.Response)
    mock_is_user_in_db_respone.status_code = 200

    products_response = MagicMock(spec=httpx.Response)
    products_response.json.return_value = expected_products
    products_response.status_code = 200

    mock_http_client.get.side_effect = [mock_is_user_in_db_respone, products_response]

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'repeater'
    mock_redis_client.get.assert_awaited_once_with('products:repeater')
    mock_http_client.get.assert_any_await('/user-data?phone=79123456789')
    mock_http_client.get.assert_any_await('/api/products?flow_type=repeater')
    mock_redis_client.set.assert_awaited_once()


def test_integration_failure_api_status_error(client_with_mocked_deps):
    test_client, mock_http_client, _ = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}

    mock_request = MagicMock(spec=httpx.Request)
    mock_response = MagicMock(spec=httpx.Response)
    mock_http_client.get.side_effect = httpx.HTTPStatusError(
        'Status Error',
        request=mock_request,
        response=mock_response
    )
    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 502
    assert response.json() == {'detail': 'Integration Error'}


def test_integration_failure_api_connect_error(client_with_mocked_deps):
    test_client, mock_http_client, _ = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}

    mock_http_client.get.side_effect = httpx.ConnectError('ConnectError')

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 503
    assert response.json() == {'detail': 'Connect Error'}


def test_wrong_phone_format_api(client_with_mocked_deps):
    test_client, _, __ = client_with_mocked_deps
    phone_data = {'phone_number': '89123456789'}

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 422


def test_pioneer_flow_with_cache_hit(client_with_mocked_deps):
    test_client, mock_http_client, mock_redis_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}
    cached_products = [{
        'product_name': 'Cached Product', 'amount': 500, 'percentage': 5.5
    }]

    mock_redis_client.get = AsyncMock(return_value=json.dumps(cached_products))
    mock_redis_client.set = AsyncMock()

    mock_is_user_in_db_respone = MagicMock(spec=httpx.Response)
    mock_is_user_in_db_respone.status_code = 404
    mock_http_client.get.side_effect = [mock_is_user_in_db_respone]

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'pioneer'
    assert response_data['available_products'] == cached_products
    mock_redis_client.get.assert_awaited_once_with('products:pioneer')
    mock_redis_client.set.assert_not_awaited()


def test_pioneer_flow_when_redis_fails(client_with_mocked_deps):
    test_client, mock_http_client, mock_redis_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}
    expected_products = [
        {'product_name': 'Test Product', 'amount': 100, 'percentage': 10.5}]

    mock_redis_client.get = AsyncMock(
        side_effect=redis.RedisError('Connection failed'))
    mock_redis_client.set = AsyncMock(
        side_effect=redis.RedisError('Connection failed'))

    mock_is_user_in_db_respone = MagicMock(
        spec=httpx.Response, status_code=404)
    products_response = MagicMock(spec=httpx.Response, status_code=200)
    products_response.json.return_value = expected_products
    mock_http_client.get.side_effect = [
        mock_is_user_in_db_respone, products_response]

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'pioneer'
    assert response_data['available_products'] == expected_products
