import pytest
from fastapi.testclient import TestClient

from app.api.scoring.schemas import ScoringRequestPioneer
from app.repository import client_repo
from app.service import app
from tests.unit.mock_scoring_data import (
    MOCK_PRODUCT_LOYALTY,
    MOCK_TEST_PROFILE_LOW_POINTS,
    MOCK_TEST_PROFILE_LOYALTY,
    MOCK_TEST_PROFILE_OPEN_CREDIT,
)

JSON_PIONEER = {
    'user_data': {
        'phone': '79123456789',
        'age': 25,
        'monthly_income': 45000,
        'employment_type': 'full_time',
        'has_property': True
    },
    'products': [
        {'name': 'MicroLoan', 'max_amount': 30000,
         'term_days': 30, 'interest_rate_daily': 2.0},
        {'name': 'QuickMoney', 'max_amount': 1500000,
         'term_days': 15, 'interest_rate_daily': 2.5}
    ]
}
MOCK_REQUEST = ScoringRequestPioneer.model_validate(JSON_PIONEER)

JSON_REPEATER = {
    'phone': '79123456789',
    'products': [{'name': 'LoyaltyLoan', 'max_amount': 30000,
                  'term_days': 100, 'interest_rate_daily': 1.6},
                 {'name': 'AdvantagePlus', 'max_amount': 60000,
                  'term_days': 100, 'interest_rate_daily': 1.4},
                 {'name': 'PrimeCredit', 'max_amount': 90000,
                  'term_days': 100, 'interest_rate_daily': 1.2}
                 ]
}


@pytest.fixture
def client():
    client_repo.CLIENT_PROFILE_DB.clear()
    test_client = TestClient(app)

    yield test_client

    client_repo.CLIENT_PROFILE_DB.clear()


@pytest.mark.asyncio
async def test_pioneer_get_product_success(client):

    response = client.post('/api/scoring/pioneer', json=JSON_PIONEER)

    assert response.status_code == 200
    data = response.json()
    assert data['decision'] == 'accepted'
    assert data['product'] == {
        'name': 'QuickMoney',
        'max_amount': 1500000,
        'term_days': 15,
        'interest_rate_daily': 2.5
    }
    assert len(client_repo.CLIENT_PROFILE_DB) == 1


@pytest.mark.asyncio
async def test_pioneer_get_product_rejected_low_income(client):
    test_request = MOCK_REQUEST.model_copy(deep=True)
    test_request.user_data.monthly_income = 5000

    response = client.post('/api/scoring/pioneer',
                           json=test_request.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data['decision'] == 'rejected'
    assert data['product'] is None
    assert len(client_repo.CLIENT_PROFILE_DB) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('user_type', ['pioneer', 'repeater'])
async def test_wrong_phone_numbers_format(client, user_type):
    phones_data = [
        {'phone_number': '79123456789a'},
        {'phone_number': '89123456789'},
        {'phone_number': '790'}
    ]

    for phone_data in phones_data:
        response = client.post(f'api/scoring/{user_type}', json=phone_data)

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_repeater_get_product_success(client):
    client_repo.CLIENT_PROFILE_DB['79123456789'] = MOCK_TEST_PROFILE_LOYALTY
    response = client.post('api/scoring/repeater', json=JSON_REPEATER)

    assert response.status_code == 200
    data = response.json()
    assert data['decision'] == 'accepted'
    assert data['product'] == MOCK_PRODUCT_LOYALTY[0].model_dump()


@pytest.mark.asyncio
async def test_repeater_get_product_reject_low_points(client):
    client_repo.CLIENT_PROFILE_DB['79123456789'] = MOCK_TEST_PROFILE_LOW_POINTS
    response = client.post('api/scoring/repeater', json=JSON_REPEATER)
    assert response.status_code == 200
    data = response.json()
    assert data['decision'] == 'rejected'
    assert data['product'] is None


@pytest.mark.asyncio
async def test_repeater_get_product_reject_open_credit(client):
    client_repo.CLIENT_PROFILE_DB['79123456789'] = MOCK_TEST_PROFILE_OPEN_CREDIT
    response = client.post('api/scoring/repeater', json=JSON_REPEATER)
    assert response.status_code == 200
    data = response.json()
    assert data['decision'] == 'rejected'
    assert data['product'] is None


@pytest.mark.asyncio
async def test_repeater_get_product_user_not_found(client):
    response = client.post('api/scoring/repeater', json=JSON_REPEATER)

    assert response.status_code == 404
