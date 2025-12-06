from datetime import date
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.antifraud.schemas import (
    LoanItem,
)
from app.core.constants import REJECT_REASON_P1
from app.core.exceptions import DataServiceNotFoundError, IntegrationError
from app.dependencies import get_antifraud_service
from app.external_services.data_service.logic.data_service import DataService
from app.external_services.redis_service.redis_service import RedisService
from app.external_services.data_service.api.schemas import (
    UserDataFromDataServiceResponse,
    UserProfileFromDataService,
)
from app.logic.antifraud_logic import AntifraudService
from app.service import app

PIONEER_URL = '/api/antifraud/pioneer/check'
REPEATER_URL = '/api/antifraud/repeater/check'
TEST_PHONE = '71231231230'

PIONEER_PASS_REQUEST = {
    'user_data': {
        'phone': TEST_PHONE,
        'age': 30,
        'monthly_income': 50000,
        'employment_type': 'full_time',
        'has_property': True,
    }
}

REPEATER_PASS_REQUEST = {
    'phone': TEST_PHONE,
    'new_updated_profile': {
        'phone': TEST_PHONE,
        'age': 30,
        'monthly_income': 50000,
        'employment_type': 'full_time',
        'has_property': True,
    },
}


MOCK_REDIS_SERVICE = AsyncMock(spec=RedisService)
MOCK_DATA_SERVICE = AsyncMock(spec=DataService)


@pytest_asyncio.fixture
async def client():
    MOCK_REDIS_SERVICE.reset_mock()
    MOCK_DATA_SERVICE.reset_mock()

    app.dependency_overrides[get_antifraud_service] = lambda: AntifraudService(
        data_service=MOCK_DATA_SERVICE, redis_service=MOCK_REDIS_SERVICE
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_pioneer_api_happy_path_passed(client):
    MOCK_REDIS_SERVICE.get_application_count.return_value = 1

    response = await client.post(PIONEER_URL, json=PIONEER_PASS_REQUEST)

    assert response.status_code == 200
    assert response.json()['decision'] == 'passed'
    MOCK_REDIS_SERVICE.increment_application_count.assert_called_once_with(TEST_PHONE)


@pytest.mark.asyncio
async def test_pioneer_api_rejected_path_limit_exceeded(client):
    """Превышениe лимита P1."""

    MOCK_REDIS_SERVICE.get_application_count.return_value = 3

    response = await client.post(PIONEER_URL, json=PIONEER_PASS_REQUEST)

    assert response.status_code == 200
    assert response.json()['decision'] == 'rejected'
    assert REJECT_REASON_P1 in response.json()['reasons']
    MOCK_REDIS_SERVICE.increment_application_count.assert_not_called()


@pytest.mark.asyncio
async def test_repeater_api_happy_path_passed(client):
    MOCK_DATA_SERVICE.get_user_profile.return_value = UserDataFromDataServiceResponse(
        phone=TEST_PHONE,
        profile=UserProfileFromDataService(
            age=30,
            monthly_income=50000,
            employment_type='full_time',
            has_property=False,
        ),
        history=[
            LoanItem(
                loan_id='id1',
                product_name='Test',
                amount=100,
                issue_date=date(2025, 11, 20),
                term_days=30,
                status='closed',
            )
        ],
    )

    response = await client.post(REPEATER_URL, json=REPEATER_PASS_REQUEST)

    assert response.status_code == 200
    assert response.json()['decision'] == 'passed'
    MOCK_DATA_SERVICE.get_user_profile.assert_called_once_with(TEST_PHONE)
    MOCK_REDIS_SERVICE.increment_application_count.assert_called_once_with(TEST_PHONE)


@pytest.mark.asyncio
async def test_repeater_api_data_service_404_error(client):
    """data-service return 404 -> обработка на 502."""

    MOCK_DATA_SERVICE.get_user_profile.side_effect = DataServiceNotFoundError()

    response = await client.post(REPEATER_URL, json=REPEATER_PASS_REQUEST)

    assert response.status_code == 502
    assert 'Integration Error' in response.json()['detail']


@pytest.mark.asyncio
async def test_pioneer_api_redis_integration_error(client):
    """Ошибка интеграции Redis -> 502"""

    MOCK_REDIS_SERVICE.get_application_count.side_effect = IntegrationError()

    response = await client.post(PIONEER_URL, json=PIONEER_PASS_REQUEST)


    assert response.status_code == 502
    assert 'Integration Error' in response.json()['detail']


@pytest.mark.asyncio
async def test_repeater_api_data_service_5xx_error(client):
    """data-service 5xx -> 502"""

    MOCK_DATA_SERVICE.get_user_profile.side_effect = IntegrationError()

    response = await client.post(REPEATER_URL, json=REPEATER_PASS_REQUEST)

    assert response.status_code == 502
    assert 'Integration Error' in response.json()['detail']

