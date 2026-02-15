from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from aiokafka.errors import KafkaError

from app.core.constants import REJECT_RESPONSE
from app.core.custom_exceptions import IntegrationError, UserNotFoundError
from app.external_service.antifraud_service import AntifraudService
from app.external_service.kafka_producer import KafkaProducerService
from app.logic.scoring import UserScoring
from tests.unit.mock_scoring_data import (
    MOCK_PRODUCTS_PIONEER,
    MOCK_PRODUCTS_REPEATER,
    MOCK_REPEATER_PROFILE_JSON,
    MOCK_USER_DATA_PIONEER_ACCEPTED,
    MOCK_USER_DATA_PIONEER_REJECTED_SCORE,
)


@pytest.fixture
def scoring_service_fixture():
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)
    mock_kafka_producer = AsyncMock(spec=KafkaProducerService)
    mock_antifraud_service = AsyncMock(spec=AntifraudService)

    mock_kafka_producer.topic = 'test_kafka_topic'
    mock_antifraud_service.check_pioneer.return_value = {'decision': 'passed', 'reasons': []}
    mock_antifraud_service.check_repeater.return_value = {'decision': 'passed', 'reasons': []}

    service = UserScoring(
        client=mock_http_client,
        kafka_producer=mock_kafka_producer,
        antifraud_service=mock_antifraud_service
    )
    return service, mock_http_client, mock_kafka_producer, mock_antifraud_service


@pytest.mark.asyncio
async def test_pioneer_accepted_sends_to_kafka(scoring_service_fixture):
    """Новый клиент одобрен, сообщение успешно отправлено в Kafka."""
    service, _, mock_kafka_producer, mock_antifraud_service = scoring_service_fixture

    result = await service.user_scoring_pioneer(
        MOCK_USER_DATA_PIONEER_ACCEPTED, MOCK_PRODUCTS_PIONEER
    )
    mock_antifraud_service.check_pioneer.assert_called_once()

    assert result['decision'] == 'accepted'
    mock_kafka_producer.send.assert_called_once()


@pytest.mark.asyncio
async def test_pioneer_rejected_by_antifraud_and_not_send_to_kafka(scoring_service_fixture):
    """Новый клиент отклонен aнтифродом, в Kafka ничего не отправляется."""
    service, _, mock_kafka_producer, mock_antifraud_service = scoring_service_fixture

    mock_antifraud_service.check_pioneer.return_value = {
        'decision': 'rejected', 'reasons': ['B1_REASON']
        }

    result = await service.user_scoring_pioneer(
        MOCK_USER_DATA_PIONEER_ACCEPTED, MOCK_PRODUCTS_PIONEER
    )

    assert result == REJECT_RESPONSE
    mock_antifraud_service.check_pioneer.assert_called_once()
    mock_kafka_producer.send.assert_not_called()


@pytest.mark.asyncio
async def test_pioneer_rejected_by_score_and_not_send_to_kafka(scoring_service_fixture):
    """Новый клиент отклонен низким скоринговым баллом"""
    service, _, mock_kafka_producer, _ = scoring_service_fixture

    result = await service.user_scoring_pioneer(
        MOCK_USER_DATA_PIONEER_REJECTED_SCORE, MOCK_PRODUCTS_PIONEER
    )

    assert result == REJECT_RESPONSE
    mock_kafka_producer.send.assert_not_called()


@pytest.mark.asyncio
async def test_pioneer_kafka_send_fails_but_returns_accepted(scoring_service_fixture):
    service, _, mock_kafka_producer, _ = scoring_service_fixture
    mock_kafka_producer.send.side_effect = KafkaError('Kafka is down')
    result = await service.user_scoring_pioneer(
        MOCK_USER_DATA_PIONEER_ACCEPTED, MOCK_PRODUCTS_PIONEER
    )
    assert result['decision'] == 'accepted'
    mock_kafka_producer.send.assert_called_once()


@pytest.mark.asyncio
async def test_pioneer_antifraud_integration_error(scoring_service_fixture):
    service, _, _, mock_antifraud_service = scoring_service_fixture

    mock_antifraud_service.check_pioneer.side_effect = IntegrationError()

    with pytest.raises(IntegrationError):
        await service.user_scoring_pioneer(
            MOCK_USER_DATA_PIONEER_ACCEPTED, MOCK_PRODUCTS_PIONEER
        )


@pytest.mark.asyncio
@patch('app.external_service.get_credit_status_service.get_credit_status', return_value='closed')
async def test_repeater_accepted_sends_to_kafka(mock_get_status, scoring_service_fixture):
    service, mock_http_client, mock_kafka_producer, mock_antifraud_service = scoring_service_fixture

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_http_client.get.return_value = mock_get_response

    result = await service.user_scoring_repeater(
        MOCK_REPEATER_PROFILE_JSON['phone'], MOCK_PRODUCTS_REPEATER
    )

    assert result['decision'] == 'accepted'
    mock_antifraud_service.check_repeater.assert_called_once()
    mock_kafka_producer.send.assert_called_once()


@pytest.mark.asyncio
async def test_repeater_user_not_found_does_not_send_to_kafka(scoring_service_fixture):
    """Повторный клиент не найден, в Kafka ничего не отправляется."""
    service, mock_http_client, mock_kafka_producer, _ = scoring_service_fixture

    mock_response = MagicMock(spec=httpx.Response, status_code=404)
    mock_http_client.get.return_value = mock_response

    with pytest.raises(UserNotFoundError):
        await service.user_scoring_repeater('71234567890', MOCK_PRODUCTS_REPEATER)

    mock_kafka_producer.send.assert_not_called()
