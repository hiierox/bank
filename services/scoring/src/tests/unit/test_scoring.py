from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config.config import Config
from app.core.constants import REJECT_RESPONSE
from app.core.custom_exceptions import LoanAlreadyExistsError, UserNotFoundError
from app.logic.scoring import UserScoring
from tests.unit.mock_scoring_data import (
    MOCK_PRODUCTS_PIONEER,
    MOCK_PRODUCTS_REPEATER,
    MOCK_REPEATER_PROFILE_JSON,
    MOCK_USER_DATA_PIONEER_ACCEPTED,
    MOCK_USER_DATA_PIONEER_REJECTED_SCORE,
    MOCK_USER_DATA_PIONEER_REJECTED_STOP_FACTOR,
)


@pytest.fixture
def config_fixture() -> Config:
    return Config.model_validate({
        'data_service': {
            'base_url': 'http://test-data-service', 'timeout': 1,
            'retries': {'max_attempts': 2, 'delay': 0}
        }
    })

@pytest.fixture
def scoring_service_fixture(config_fixture):
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)
    service = UserScoring(client=mock_http_client, config=config_fixture)
    return service, mock_http_client


@pytest.mark.asyncio
async def test_pioneer_accepted_and_saved(scoring_service_fixture):
    service, mock_client = scoring_service_fixture
    mock_response = MagicMock(spec=httpx.Response, status_code=201)
    mock_client.put.return_value = mock_response

    result = await service.user_scoring_pioneer(MOCK_USER_DATA_PIONEER_ACCEPTED, MOCK_PRODUCTS_PIONEER)

    assert result['decision'] == 'accepted'
    assert result['product'] is not None
    mock_client.put.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize('user_data', [
    MOCK_USER_DATA_PIONEER_REJECTED_SCORE,
    MOCK_USER_DATA_PIONEER_REJECTED_STOP_FACTOR,
])
async def test_pioneer_rejected_before_scoring(scoring_service_fixture, user_data):
    service, mock_client = scoring_service_fixture

    result = await service.user_scoring_pioneer(user_data, MOCK_PRODUCTS_PIONEER)

    assert result == REJECT_RESPONSE
    mock_client.put.assert_not_called()


@pytest.mark.asyncio
@patch('app.logic.scoring.get_credit_status', return_value='closed')
async def test_repeater_accepted_and_updated(mock_get_credit_status, scoring_service_fixture):
    service, mock_client = scoring_service_fixture

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON
    mock_put_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_client.get.return_value = mock_get_response
    mock_client.put.return_value = mock_put_response

    result = await service.user_scoring_repeater(MOCK_REPEATER_PROFILE_JSON['phone'], MOCK_PRODUCTS_REPEATER)

    assert result['decision'] == 'accepted'
    assert result['product'] is not None
    mock_client.get.assert_called_once()
    mock_client.put.assert_called_once()


@pytest.mark.asyncio
async def test_repeater_user_not_found(scoring_service_fixture):
    service, mock_client = scoring_service_fixture
    mock_response = MagicMock(spec=httpx.Response, status_code=404)
    mock_client.get.return_value = mock_response

    with pytest.raises(UserNotFoundError):
        await service.user_scoring_repeater('71234567890', MOCK_PRODUCTS_REPEATER)


@pytest.mark.asyncio
@patch('app.logic.scoring.get_credit_status', return_value='closed')
async def test_repeater_update_fails(mock_get_credit_status, scoring_service_fixture):
    service, mock_client = scoring_service_fixture

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON

    mock_put_response = MagicMock(spec=httpx.Response, status_code=500)
    mock_put_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        'Server Error', request=MagicMock(), response=mock_put_response
    )

    mock_client.get.return_value = mock_get_response
    mock_client.put.return_value = mock_put_response

    with pytest.raises(httpx.HTTPStatusError):
        await service.user_scoring_repeater(MOCK_REPEATER_PROFILE_JSON['phone'], MOCK_PRODUCTS_REPEATER)


@pytest.mark.asyncio
@patch('app.logic.scoring.get_credit_status', return_value='closed')
async def test_repeater_loan_already_exists(mock_get_credit_status, scoring_service_fixture):
    service, mock_client = scoring_service_fixture

    mock_get_response = MagicMock(spec=httpx.Response, status_code=200)
    mock_get_response.json.return_value = MOCK_REPEATER_PROFILE_JSON

    mock_put_response = MagicMock(spec=httpx.Response, status_code=422)

    mock_client.get.return_value = mock_get_response
    mock_client.put.return_value = mock_put_response

    with pytest.raises(LoanAlreadyExistsError):
        await service.user_scoring_repeater(MOCK_REPEATER_PROFILE_JSON['phone'], MOCK_PRODUCTS_REPEATER)

