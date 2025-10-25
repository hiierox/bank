from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_http_client
from app.service import app


@pytest.fixture
def client_with_mocked_deps():
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)

    def override_get_http_client() -> httpx.AsyncClient:
        return mock_http_client

    app.dependency_overrides[get_http_client] = override_get_http_client
    test_client = TestClient(app)

    yield test_client, mock_http_client

    del app.dependency_overrides[get_http_client]


def test_pioneer_flow_api(client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_http_client.get.return_value = mock_response

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'pioneer'
    assert 'available_products' in response_data


def test_repeater_flow_api(client_with_mocked_deps):

    test_client, mock_http_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_http_client.get.return_value = mock_response

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'repeater'


def test_integration_failure_api_status_error(client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps
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
    test_client, mock_http_client = client_with_mocked_deps
    phone_data = {'phone_number': '79123456789'}

    mock_http_client.get.side_effect = httpx.ConnectError('ConnectError')

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 503
    assert response.json() == {'detail': 'Connect Error'}


def test_wrong_phone_format_api(client_with_mocked_deps):
    test_client, _ = client_with_mocked_deps
    phone_data = {'phone_number': '89123456789'}

    response = test_client.post('/api/products', json=phone_data)

    assert response.status_code == 422
