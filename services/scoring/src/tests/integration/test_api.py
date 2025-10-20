import pytest
from fastapi.testclient import TestClient

from app.api.scoring.schemas import ScoringRequest
from app.repository import client_repo
from app.service import app

JSON = {
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
MOCK_REQUEST = ScoringRequest.model_validate(JSON)


@pytest.fixture
def client():
    client_repo.user_data_db.clear()
    test_client = TestClient(app)

    yield test_client

    client_repo.user_data_db.clear()


@pytest.mark.asyncio
async def test_pioneer_get_product_success(client):

    response = client.post('/api/scoring/pioneer', json=JSON)

    assert response.status_code == 200
    data = response.json()
    assert data['decision'] == 'accepted'
    assert data['product'] == {
        'name': 'QuickMoney',
        'max_amount': 1500000,
        'term_days': 15,
        'interest_rate_daily': 2.5
    }
    assert len(client_repo.user_data_db) == 1


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
    assert len(client_repo.user_data_db) == 0


@pytest.mark.asyncio
async def test_wrong_phone_numbers_format(client):
    phones_data = [
        {'phone_number': '79123456789a'},
        {'phone_number': '89123456789'},
        {'phone_number': '790'}
    ]

    for phone_data in phones_data:
        response = client.post('api/scoring/pioneer', json=phone_data)

        assert response.status_code == 422
