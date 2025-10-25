from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_http_client
from app.service import app
from tests.unit.mock_scoring_data import (
    MOCK_PRODUCTS_PIONEER,
    MOCK_PRODUCTS_REPEATER,
    MOCK_REPEATER_PROFILE_JSON,
    MOCK_USER_DATA_PIONEER_ACCEPTED,
)


@pytest.fixture
def client_with_mocked_deps():
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)

    def override_get_http_client() -> httpx.AsyncClient:
        return mock_http_client

    app.dependency_overrides[get_http_client] = override_get_http_client
    test_client = TestClient(app)
    yield test_client, mock_http_client
    del app.dependency_overrides[get_http_client]


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_rejected_api(mock_get_status, client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_put_response = MagicMock(spec=httpx.Response, status_code=200)

    mock_http_client.get.return_value = mock_get_response
    mock_http_client.put.return_value = mock_put_response

    request_data = {
        'phone': MOCK_REPEATER_PROFILE_JSON['phone'], 'products': []}
    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 200
    assert response.json()['decision'] == 'rejected'
    mock_http_client.get.assert_called_once()


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_accepted_api(mock_get_status, client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_put_response = MagicMock(spec=httpx.Response, status_code=200)

    mock_http_client.get.return_value = mock_get_response
    mock_http_client.put.return_value = mock_put_response

    request_data = {
        'phone': MOCK_REPEATER_PROFILE_JSON['phone'],
        'products': [p.model_dump() for p in MOCK_PRODUCTS_REPEATER]
    }
    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 200
    assert response.json()['decision'] == 'accepted'


def test_pioneer_data_service_fails_api(client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps
    mock_http_client.put.side_effect = httpx.TimeoutException(
        'Connection failed')

    request_data = {
        'user_data': MOCK_USER_DATA_PIONEER_ACCEPTED.model_dump(),
        'products': [p.model_dump() for p in MOCK_PRODUCTS_PIONEER]
    }
    response = test_client.post('/api/scoring/pioneer', json=request_data)

    assert response.status_code == 500
    assert response.json()['detail'] == 'InternalServerError'


def test_pioneer_validation_error_api(client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    invalid_data = {
        'user_data': {'phone': '71234567890', 'age': -1},
        'products': []
    }
    response = test_client.post('/api/scoring/pioneer', json=invalid_data)

    assert response.status_code == 422
    mock_http_client.put.assert_not_called()


def test_repeater_user_not_found_api(client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    mock_response = MagicMock(spec=httpx.Response, status_code=404)
    mock_http_client.get.return_value = mock_response

    request_data = {'phone': '71112223344', 'products': []}
    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 404
    assert response.json()['detail'] == 'UserNotFoundError'


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_update_fails_api(mock_get_status, client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_http_client.get.return_value = mock_get_response

    mock_http_client.put.side_effect = httpx.ConnectError('ConnectionError')

    request_data = {
        'phone': MOCK_REPEATER_PROFILE_JSON['phone'],
        'products': [p.model_dump() for p in MOCK_PRODUCTS_REPEATER]
    }
    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 503


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_data_service_internal_error_returns_502(mock_get_status, client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_http_client.get.return_value = mock_get_response

    http_error = httpx.HTTPStatusError(
        'Server Error',
        request=MagicMock(spec=httpx.Request),
        response=MagicMock(spec=httpx.Response, status_code=500)
    )
    mock_http_client.put.side_effect = http_error

    request_data = {
        'phone': MOCK_REPEATER_PROFILE_JSON['phone'],
        'products': [p.model_dump() for p in MOCK_PRODUCTS_REPEATER]
    }
    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 502
    assert response.json() == {'detail': 'UpdateError'}


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_loan_already_exists_returns_502(mock_get_status, client_with_mocked_deps):
    test_client, mock_http_client = client_with_mocked_deps

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_http_client.get.return_value = mock_get_response

    mock_put_response = MagicMock(spec=httpx.Response, status_code=422)
    mock_http_client.put.return_value = mock_put_response

    request_data = {
        'phone': MOCK_REPEATER_PROFILE_JSON['phone'],
        'products': [p.model_dump() for p in MOCK_PRODUCTS_REPEATER]
    }
    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 502
    assert response.json() == {'detail': 'LoanAlreadyExistsError'}
