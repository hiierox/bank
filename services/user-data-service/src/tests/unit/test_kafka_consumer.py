from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.external_services.kafka_consumer import KafkaConsumerService

PIONEER_MESSAGE = {
    'version': 1,
    'event': 'pioneer_accepted',
    'phone': '79112223344',
    'profile': {
        'age': 30,
        'monthly_income': 50000,
        'employment_type': 'full_time',
        'has_property': True
    },

    'history_entry': {
        'loan_id': 'pioneer_loan_1', 'product_name': 'QuickMoney', 'amount': 100,
        'issue_date': '2025-01-01', 'term_days': 30, 'status': 'open'
    }
}

REPEATER_MESSAGE = {
    'version': 1,
    'event': 'repeater_accepted',
    'phone': '79556667788',
    'profile': {
        'age': 41,
        'monthly_income': 90000,
        'employment_type': 'full_time',
        'has_property': True
    },
    'history_entry': {
        'loan_id': 'repeater_loan_1', 'product_name': 'LoayltyLoan', 'amount': 200,
        'issue_date': '2025-01-02', 'term_days': 60, 'status': 'open'
    }
}


@pytest.fixture
def mock_kafka_dependencies():
    """
    Фикстура, которая патчит UserDataService
    """
    with patch(
        'app.external_services.kafka_consumer.UserDataService', autospec=True
    ) as MockUserDataService:

        mock_service_instance = AsyncMock()
        MockUserDataService.return_value = mock_service_instance

        yield mock_service_instance


@pytest.fixture
def consumer_service():
    """
    Фикстура, создающая экземпляр KafkaConsumerService
    c замоканным AIOKafkaConsumer
    """
    with patch('app.external_services.kafka_consumer.AIOKafkaConsumer'):
        mock_config = MagicMock()
        service = KafkaConsumerService(config=mock_config)
        yield service


@pytest.mark.asyncio
async def test_process_pioneer_message_success(consumer_service, mock_kafka_dependencies):
    """Успешная обработка сообщения o новом клиенте."""
    mock_data_service = mock_kafka_dependencies

    await consumer_service.process_message(PIONEER_MESSAGE)

    mock_data_service.put_user_data.assert_awaited_once()
    call_args, _ = mock_data_service.put_user_data.call_args
    assert call_args[0] == PIONEER_MESSAGE['phone']
    assert call_args[1].profile is not None and call_args[1].profile.age == 30
    assert call_args[1].loan_entry.loan_id == 'pioneer_loan_1'


@pytest.mark.asyncio
async def test_process_repeater_message_success(consumer_service, mock_kafka_dependencies):
    """Успешная обработка сообщения o повторном клиенте."""
    mock_data_service = mock_kafka_dependencies

    await consumer_service.process_message(REPEATER_MESSAGE)

    mock_data_service.put_user_data.assert_awaited_once()
    call_args, _ = mock_data_service.put_user_data.call_args
    assert call_args[0] == REPEATER_MESSAGE['phone']
    assert call_args[1].profile.age == 41
    assert call_args[1].profile.monthly_income == 90000


@pytest.mark.asyncio
async def test_skip_message_with_unsupported_version(consumer_service, mock_kafka_dependencies):
    """Сообщение c неверной версией"""
    mock_data_service = mock_kafka_dependencies
    invalid_message = PIONEER_MESSAGE.copy()
    invalid_message['version'] = 2

    await consumer_service.process_message(invalid_message)

    mock_data_service.put_user_data.assert_not_called()


@pytest.mark.asyncio
async def test_skip_message_with_missing_required_field(consumer_service, mock_kafka_dependencies):
    """Сообщение c отсутствующим обязательным полем phone"""
    mock_data_service = mock_kafka_dependencies
    invalid_message = PIONEER_MESSAGE.copy()
    del invalid_message['phone']

    await consumer_service.process_message(invalid_message)

    mock_data_service.put_user_data.assert_not_called()


@pytest.mark.asyncio
async def test_skip_message_with_invalid_pydantic_data(consumer_service, mock_kafka_dependencies):
    """Сообщение c невалидными данными игнорируется"""
    mock_data_service = mock_kafka_dependencies
    invalid_message = PIONEER_MESSAGE.copy()
    invalid_message['history_entry']['amount'] = 'string' # type: ignore

    await consumer_service.process_message(invalid_message)

    mock_data_service.put_user_data.assert_not_called()
