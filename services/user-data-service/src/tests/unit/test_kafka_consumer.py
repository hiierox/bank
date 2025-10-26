from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.custom_exceptions import LoanAlreadyExistError
from app.external_services.kafka_consumer import KafkaConsumerService
from app.logic.data_service import UserDataService


@pytest.fixture
async def mock_data_service() -> AsyncMock:
    return AsyncMock(spec=UserDataService)


@pytest.fixture
async def consumer_service(mock_data_service: AsyncMock) -> KafkaConsumerService:
    mock_config = MagicMock()
    return KafkaConsumerService(config=mock_config, data_service=mock_data_service)


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


@pytest.mark.asyncio
async def test_process_pioneer_message_success(
    consumer_service: KafkaConsumerService,
    mock_data_service: AsyncMock
):
    """Успешная обработка сообщения pioneer_accepted."""
    await consumer_service.process_message(PIONEER_MESSAGE)

    mock_data_service.put_user_data.assert_called_once()
    call_args = mock_data_service.put_user_data.call_args
    assert call_args.args[0] == PIONEER_MESSAGE['phone']
    assert call_args.args[1].profile is not None


@pytest.mark.asyncio
async def test_process_repeater_message_success(
    consumer_service: KafkaConsumerService,
    mock_data_service: AsyncMock
):
    """Успешная обработка сообщения repeater_accepted."""
    await consumer_service.process_message(REPEATER_MESSAGE)

    mock_data_service.put_user_data.assert_called_once()


@pytest.mark.asyncio
async def test_skip_message_with_unsupported_version(
    consumer_service: KafkaConsumerService,
    mock_data_service: AsyncMock
):
    """Сообщение c неверной версией игнорируется."""
    invalid_message = PIONEER_MESSAGE.copy()
    invalid_message['version'] = 2

    await consumer_service.process_message(invalid_message)

    mock_data_service.put_user_data.assert_not_called()


@pytest.mark.asyncio
async def test_skip_message_with_missing_fields(
    consumer_service: KafkaConsumerService,
    mock_data_service: AsyncMock
):
    """Сообщение c отсутствующими полями игнорируется."""
    invalid_message = PIONEER_MESSAGE.copy()
    del invalid_message['phone']

    await consumer_service.process_message(invalid_message)

    mock_data_service.put_user_data.assert_not_called()


@pytest.mark.asyncio
async def test_ignore_loan_already_exists_error(
    consumer_service: KafkaConsumerService,
    mock_data_service: AsyncMock
):
    """Ошибка LoanAlreadyExistError логируется, но сервис не падает."""
    mock_data_service.put_user_data.side_effect = LoanAlreadyExistError

    await consumer_service.process_message(PIONEER_MESSAGE)

    mock_data_service.put_user_data.assert_called_once()


@pytest.mark.asyncio
async def test_re_raise_other_exceptions(
    consumer_service: KafkaConsumerService,
    mock_data_service: AsyncMock
):
    """Любая ошибка пробрасывается наверх."""
    mock_data_service.put_user_data.side_effect = ValueError(
        'Error')

    with pytest.raises(ValueError):
        await consumer_service.process_message(PIONEER_MESSAGE)

    mock_data_service.put_user_data.assert_called_once()
