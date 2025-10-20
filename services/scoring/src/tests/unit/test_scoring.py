from unittest.mock import AsyncMock

import pytest

from app.api.scoring.schemas import Product, UserData
from app.logic.scoring import UserScoring
from app.repository.client_repo import ClientProfileRepository

MOCK_USER_DATA_SUCCESS = UserData(
    phone='79123456789',
    age=25,
    monthly_income=45000,
    employment_type='full_time',
    has_property=True
)
MOCK_USER_DATA_REJECT = UserData(
    phone='79123456789',
    age=25,
    monthly_income=45000,
    employment_type='freelance',
    has_property=False
)
MOCK_USER_DATA_FAIL = UserData(
    phone='79123456789',
    age=15,
    monthly_income=45000,
    employment_type='freelance',
    has_property=False
)
MOCK_PRODUCTS = [
    Product(name='MicroLoan', max_amount=3000000,
            term_days=30, interest_rate_daily=2.0),
    Product(name='QuickMoney', max_amount=1500000,
            term_days=15, interest_rate_daily=2.5),
    Product(name='ConsumerLoan', max_amount=4500000,
            term_days=15, interest_rate_daily=2.5)
]


@pytest.fixture
def user_scoring_fixture():
    mock_client_repo = AsyncMock(spec=ClientProfileRepository)
    scoring_service = UserScoring(mock_client_repo)
    return mock_client_repo, scoring_service


@pytest.mark.asyncio
async def test_user_scoring_accepted_quickmoney(user_scoring_fixture):
    client_repo, scoring_service = user_scoring_fixture

    result = await scoring_service.user_scoring(user_data=MOCK_USER_DATA_SUCCESS,
                                                products=MOCK_PRODUCTS)

    assert result['decision'] == 'accepted'
    assert result['product'].model_dump() == MOCK_PRODUCTS[1].model_dump()
    client_repo.save_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_user_scoring_rejected_low_score(user_scoring_fixture):
    client_repo, scoring_service = user_scoring_fixture

    result = await scoring_service.user_scoring(user_data=MOCK_USER_DATA_REJECT,
                                                products=MOCK_PRODUCTS)

    assert result['decision'] == 'rejected'
    assert result['product'] is None
    client_repo.save_user_profile.assert_not_called()


@pytest.mark.asyncio
async def test_user_scoring_rejected_fail(user_scoring_fixture):
    client_repo, scoring_service = user_scoring_fixture

    result = await scoring_service.user_scoring(user_data=MOCK_USER_DATA_FAIL,
                                                products=MOCK_PRODUCTS)

    assert result['decision'] == 'rejected'
    assert result['product'] is None
    client_repo.save_user_profile.assert_not_called()
