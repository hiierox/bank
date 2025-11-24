from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from aiokafka.errors import KafkaError
from fastapi.testclient import TestClient

from app.dependencies import get_http_client, get_kafka_producer_service
from app.external_service.kafka_producer import KafkaProducerService
from app.service import app
from tests.unit.mock_scoring_data import (
    MOCK_PRODUCTS_PIONEER,
    MOCK_PRODUCTS_REPEATER,
    MOCK_REPEATER_PROFILE_JSON,
    MOCK_USER_DATA_PIONEER_ACCEPTED,
    MOCK_USER_DATA_PIONEER_REJECTED_SCORE,
)


@pytest.fixture
def client_with_mocked_deps():
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)
    mock_kafka_producer = AsyncMock(spec=KafkaProducerService)
    mock_kafka_producer.topic = "test_kafka_topic"

    app.dependency_overrides[get_http_client] = lambda: mock_http_client
    app.dependency_overrides[get_kafka_producer_service] = lambda: mock_kafka_producer

    test_client = TestClient(app)
    yield test_client, mock_http_client, mock_kafka_producer

    del app.dependency_overrides[get_http_client]
    del app.dependency_overrides[get_kafka_producer_service]


def test_pioneer_accepted_api(client_with_mocked_deps):
    """Pioneer успех, 'accepted', отправка в Kafka."""
    test_client, _, mock_kafka = client_with_mocked_deps
    request_data = {
        'user_data': MOCK_USER_DATA_PIONEER_ACCEPTED.model_dump(),
        'products': [p.model_dump() for p in MOCK_PRODUCTS_PIONEER]
    }

    response = test_client.post('/api/scoring/pioneer', json=request_data)

    assert response.status_code == 200
    assert response.json()['decision'] == 'accepted'
    mock_kafka.send.assert_called_once()


def test_pioneer_rejected_api(client_with_mocked_deps):
    """Pioneer отказ по скорингу, в Kafka ничего не отправляется."""
    test_client, _, mock_kafka = client_with_mocked_deps
    request_data = {
        'user_data': MOCK_USER_DATA_PIONEER_REJECTED_SCORE.model_dump(),
        'products': [p.model_dump() for p in MOCK_PRODUCTS_PIONEER]
    }

    response = test_client.post('/api/scoring/pioneer', json=request_data)

    assert response.status_code == 200
    assert response.json()['decision'] == 'rejected'
    mock_kafka.send.assert_not_called()


def test_pioneer_kafka_fails_api(client_with_mocked_deps):
    """Pioneer ошибка Kafka, но ответ клиенту все равно 200"""
    test_client, _, mock_kafka = client_with_mocked_deps
    mock_kafka.send.side_effect = KafkaError('Kafka is down')
    request_data = {
        'user_data': MOCK_USER_DATA_PIONEER_ACCEPTED.model_dump(),
        'products': [p.model_dump() for p in MOCK_PRODUCTS_PIONEER]
    }

    response = test_client.post('/api/scoring/pioneer', json=request_data)

    assert response.status_code == 200
    assert response.json()['decision'] == 'accepted'
    mock_kafka.send.assert_called_once()


def test_pioneer_validation_error_api(client_with_mocked_deps):
    """Pioneer ошибка валидации Pydantic, статус 422."""
    test_client, _, mock_kafka = client_with_mocked_deps
    invalid_data = {'user_data': {'phone': 'invalid-phone'}, 'products': []}

    response = test_client.post('/api/scoring/pioneer', json=invalid_data)

    assert response.status_code == 422
    mock_kafka.send.assert_not_called()


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_accepted_api(mock_get_status, client_with_mocked_deps):
    """Repeater успех, accepted, отправка в Kafka."""
    test_client, mock_http, mock_kafka = client_with_mocked_deps
    mock_get_response = MagicMock(
        spec=httpx.Response, status_code=200, json=lambda: MOCK_REPEATER_PROFILE_JSON)
    mock_http.get.return_value = mock_get_response
    request_data = {
        'phone': MOCK_REPEATER_PROFILE_JSON['phone'],
        'products': [p.model_dump() for p in MOCK_PRODUCTS_REPEATER]
    }

    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 200
    assert response.json()['decision'] == 'accepted'
    mock_http.get.assert_called_once()
    mock_kafka.send.assert_called_once()


def test_repeater_user_not_found_api(client_with_mocked_deps):
    """Repeater пользователь не найден, статус 404."""
    test_client, mock_http, mock_kafka = client_with_mocked_deps
    mock_response = MagicMock(spec=httpx.Response, status_code=404)
    mock_http.get.return_value = mock_response
    request_data = {'phone': '71112223344', 'products': []}

    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 404
    mock_kafka.send.assert_not_called()


@patch('app.logic.scoring.get_credit_status', return_value='closed')
def test_repeater_data_service_fails_api(mock_get_status, client_with_mocked_deps):
    """Repeater ошибка GET-запроса к data-service, статус 500."""
    test_client, mock_http, mock_kafka = client_with_mocked_deps
    mock_http.get.side_effect = httpx.ConnectError('Connection failed')
    request_data = {
        'phone': '71112223344',
        'products': [p.model_dump() for p in MOCK_PRODUCTS_REPEATER]
    }

    response = test_client.post('/api/scoring/repeater', json=request_data)

    assert response.status_code == 500
    mock_kafka.send.assert_not_called()
