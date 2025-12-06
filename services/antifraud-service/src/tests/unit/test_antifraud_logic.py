from unittest.mock import AsyncMock, patch

import pytest

from app.api.antifraud.schemas import (
    PioneerCheckRequest,
    RepeaterCheckRequest,
    UserProfileData,
)
from app.core.exceptions import DataServiceNotFoundError
from app.external_services.data_service.logic.data_service import DataService
from app.external_services.redis_service.redis_service import RedisService
from app.logic.antifraud_logic import AntifraudService


@pytest.fixture
def mock_redis_service():
    mock = AsyncMock(spec=RedisService)
    mock.get_application_count.return_value = 1
    return mock


@pytest.fixture
def mock_data_service():
    return AsyncMock(spec=DataService)


@pytest.fixture
def antifraud_service(mock_data_service, mock_redis_service):
    return AntifraudService(
        data_service=mock_data_service, redis_service=mock_redis_service
    )


@pytest.fixture
def mock_pioneer_request():
    return PioneerCheckRequest(
        user_data=UserProfileData(
            phone='79000000001',
            age=30,
            monthly_income=50000,
            employment_type='full_time',
            has_property=False,
        )
    )


@pytest.fixture
def mock_repeater_request():
    return RepeaterCheckRequest(
        phone='79000000002',
        new_updated_profile=UserProfileData(
            phone='79000000002',
            age=30,
            monthly_income=50000,
            employment_type='full_time',
            has_property=False,
        ),
    )



@patch('app.logic.check_rules.CommonChecks.run', return_value=[])
@patch('app.logic.check_rules.PioneerChecks.run', return_value=[])
@pytest.mark.asyncio
async def test_pioneer_check_passed(
    mock_pioneer_checks, mock_common_checks, antifraud_service, mock_pioneer_request
):
    """Bce проверки пройдены и счетчик в Redis увеличен."""

    result = await antifraud_service.check_pioneer(mock_pioneer_request)

    assert result.decision == 'passed'
    assert result.reasons == []

    antifraud_service.redis_service.increment_application_count.assert_called_once_with(
        mock_pioneer_request.user_data.phone
    )


@patch('app.logic.check_rules.CommonChecks.run', return_value=['B1_REASON'])
@patch('app.logic.check_rules.PioneerChecks.run', return_value=['P1_REASON'])
@pytest.mark.asyncio
async def test_pioneer_check_rejected(
    mock_pioneer_checks, mock_common_checks, antifraud_service, mock_pioneer_request
):
    """Проверки вернули причины и инкремент Redis не вызван."""

    result = await antifraud_service.check_pioneer(mock_pioneer_request)

    assert result.decision == 'rejected'
    expected_reasons = ['B1_REASON', 'P1_REASON']
    assert result.reasons == expected_reasons
    antifraud_service.redis_service.increment_application_count.assert_not_called()


@patch('app.logic.check_rules.CommonChecks.run', return_value=[])
@patch('app.logic.check_rules.RepeaterChecks.run', return_value=[])
@pytest.mark.asyncio
async def test_repeater_check_passed(
    mock_repeater_checks, mock_common_checks, antifraud_service, mock_repeater_request
):
    """data-service вызван, проверки пройдены -> инкремент Redis вызван."""
    result = await antifraud_service.check_repeater(mock_repeater_request)

    assert result.decision == 'passed'

    antifraud_service.data_service.get_user_profile.assert_called_once_with(
        mock_repeater_request.phone
    )
    antifraud_service.redis_service.increment_application_count.assert_called_once()


@patch('app.logic.check_rules.CommonChecks.run', return_value=[])
@patch('app.logic.check_rules.RepeaterChecks.run', return_value=['R1_REASON'])
@pytest.mark.asyncio
async def test_repeater_check_rejected(
    mock_repeater_checks, mock_common_checks, antifraud_service, mock_repeater_request
):
    """Проверки вернули причины -> инкремент Redis не вызван."""

    result = await antifraud_service.check_repeater(mock_repeater_request)

    assert result.decision == 'rejected'
    antifraud_service.redis_service.increment_application_count.assert_not_called()


@pytest.mark.asyncio
async def test_repeater_check_data_service_user_not_found(
    antifraud_service, mock_repeater_request
):
    """data-service вернул DataServiceNotFoundError"""

    antifraud_service.data_service.get_user_profile.side_effect = DataServiceNotFoundError()

    with pytest.raises(DataServiceNotFoundError):
        await antifraud_service.check_repeater(mock_repeater_request)

    antifraud_service.data_service.get_user_profile.assert_called_once()
    antifraud_service.redis_service.increment_application_count.assert_not_called()
