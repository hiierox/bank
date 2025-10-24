from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api.user_data.schemas import LoanEntryItem, LoanEntryUpdate, UserProfile
from app.repository.client_repo import USER_PROFILE_DB
from app.service import app

MOCK_PHONE = '79123456789'
MOCK_USER_PROFILE = UserProfile(
    age=30,
    monthly_income=50000,
    employment_type='full_time',
    has_property=True
)
MOCK_LOAN_ENTRY = LoanEntryItem(
    loan_id='loan_20250115_001',
    product_name='LoyaltyLoan',
    amount=50000,
    issue_date=date(2025, 1, 15),
    term_days=90,
    status='open',
    close_date=None
)
MOCK_LOAN_UPDATE = LoanEntryUpdate(
    loan_id='loan_20250115_001',
    status='closed',
    close_date=date(2025, 4, 15)
)


@pytest.fixture
def client():
    USER_PROFILE_DB.clear()
    test_client = TestClient(app)
    yield test_client
    USER_PROFILE_DB.clear()


@pytest.mark.asyncio
async def test_get_user_data_success(client):
    USER_PROFILE_DB[MOCK_PHONE] = {
        'profile': MOCK_USER_PROFILE, 'history': [MOCK_LOAN_ENTRY]}

    response = client.get(f'/user-data?phone={MOCK_PHONE}')

    assert response.status_code == 200
    assert response.json() == {
        'phone': MOCK_PHONE,
        'profile': {
            'age': 30,
            'monthly_income': 50000,
            'employment_type': 'full_time',
            'has_property': True
        },
        'history': [
            {
                'loan_id': 'loan_20250115_001',
                'product_name': 'LoyaltyLoan',
                'amount': 50000,
                'issue_date': '2025-01-15',
                'term_days': 90,
                'status': 'open',
                'close_date': None
            }
        ]
    }


@pytest.mark.asyncio
async def test_get_user_data_not_found(client):
    response = client.get('/user-data?phone=79999999999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_get_user_data_invalid_phone(client):
    response = client.get('/user-data?phone=12345')

    assert response.status_code == 422
    assert response.json()['detail'] == 'Invalid phone format'


@pytest.mark.asyncio
async def test_put_user_data_create_profile(client):
    assert len(USER_PROFILE_DB) == 0
    request_data = {
        'phone': '71291221231',
        'profile': {
            'age': 21,
            'monthly_income': 44000,
            'employment_type': 'freelance',
            'has_property': False
        },
        'loan_entry': None
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 201
    assert len(USER_PROFILE_DB) == 1


@pytest.mark.asyncio
async def test_put_user_data_update_profile(client):
    USER_PROFILE_DB[MOCK_PHONE] = {'profile': MOCK_USER_PROFILE, 'history': []}
    new_profile = {
        'age': 31,
        'monthly_income': 60000,
        'employment_type': 'freelance',
        'has_property': False
    }
    request_data = {'phone': MOCK_PHONE,
                    'profile': new_profile, 'loan_entry': None}

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 200
    assert USER_PROFILE_DB[MOCK_PHONE]['profile'].age == 31
    assert USER_PROFILE_DB[MOCK_PHONE]['profile'].monthly_income == 60000
    assert USER_PROFILE_DB[MOCK_PHONE]['profile'].employment_type == 'freelance'
    assert USER_PROFILE_DB[MOCK_PHONE]['profile'].has_property is False


@pytest.mark.asyncio
async def test_put_user_data_add_loan_entry(client):
    USER_PROFILE_DB[MOCK_PHONE] = {'profile': MOCK_USER_PROFILE, 'history': []}
    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            'loan_id': 'loan_20250115_001',
            'product_name': 'LoyaltyLoan',
            'amount': 50000,
            'issue_date': '2025-01-15',
            'term_days': 90,
            'status': 'open',
            'close_date': None
        }
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 200
    assert len(USER_PROFILE_DB[MOCK_PHONE]['history']) == 1
    assert USER_PROFILE_DB[MOCK_PHONE]['history'][0] == MOCK_LOAN_ENTRY


@pytest.mark.asyncio
async def test_put_user_data_update_loan_entry(client):
    USER_PROFILE_DB[MOCK_PHONE] = {
        'profile': MOCK_USER_PROFILE, 'history': [MOCK_LOAN_ENTRY]}
    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            'loan_id': 'loan_20250115_001',
            'status': 'closed',
            'close_date': '2025-04-15'
        }
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 200
    assert USER_PROFILE_DB[MOCK_PHONE]['history'][0].status == 'closed'
    assert USER_PROFILE_DB[MOCK_PHONE]['history'][0].close_date == date(
        2025, 4, 15)


@pytest.mark.asyncio
async def test_put_user_data_combined_update(client):
    request_data = {
        'phone': MOCK_PHONE,
        'profile': {
            'age': 30,
            'monthly_income': 50000,
            'employment_type': 'full_time',
            'has_property': True
        },
        'loan_entry': {
            'loan_id': 'loan_20250115_001',
            'product_name': 'LoyaltyLoan',
            'amount': 50000,
            'issue_date': '2025-01-15',
            'term_days': 90,
            'status': 'open',
            'close_date': None
        }
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 201
    assert len(USER_PROFILE_DB) == 1
    assert USER_PROFILE_DB[MOCK_PHONE]['profile'] == MOCK_USER_PROFILE
    assert len(USER_PROFILE_DB[MOCK_PHONE]['history']) == 1
    assert USER_PROFILE_DB[MOCK_PHONE]['history'][0] == MOCK_LOAN_ENTRY


@pytest.mark.asyncio
async def test_put_user_data_user_not_found_for_loan(client):
    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            'loan_id': 'loan_20250115_001',
            'product_name': 'LoyaltyLoan',
            'amount': 50000,
            'issue_date': '2025-01-15',
            'term_days': 90,
            'status': 'open',
            'close_date': None
        }
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_put_user_data_loan_already_exists(client):
    USER_PROFILE_DB[MOCK_PHONE] = {
        'profile': MOCK_USER_PROFILE, 'history': [MOCK_LOAN_ENTRY]}
    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            'loan_id': 'loan_20250115_001',
            'product_name': 'LoyaltyLoan',
            'amount': 50000,
            'issue_date': '2025-01-15',
            'term_days': 90,
            'status': 'open',
            'close_date': None
        }
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 422
    assert response.json() == {'detail': 'Loan already exists'}


@pytest.mark.asyncio
async def test_put_user_data_loan_not_found(client):
    USER_PROFILE_DB[MOCK_PHONE] = {'profile': MOCK_USER_PROFILE, 'history': []}
    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            'loan_id': 'loan_20250115_001',
            'status': 'closed',
            'close_date': '2025-04-15'
        }
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 404
    assert response.json() == {'detail': 'Loan not found'}


@pytest.mark.asyncio
async def test_put_user_data_invalid_data(client):
    request_data = {
        'phone': MOCK_PHONE,
        'profile': {
            'age': -1,
            'monthly_income': 50000,
            'employment_type': 'full_time',
            'has_property': True
        },
        'loan_entry': None
    }

    response = client.put('/user-data', json=request_data)

    assert response.status_code == 422
