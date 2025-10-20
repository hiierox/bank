from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.api.scoring.schemas import CreditHistoryItem, Product, UserData
from app.repository.client_repo import CLIENT_PROFILE_DB, ClientProfileRepository

MOCK_USER_DATA = UserData(
    phone='79123456789',
    age=25,
    monthly_income=45000,
    employment_type='full_time',
    has_property=True
)
MOCK_CREDIT_ITEM = CreditHistoryItem(
            product_name='MicroLoan',
            amount=30000,
            issue_date=datetime.now(tz=ZoneInfo('UTC')).date(),
            term_days=30,
            status='open',
            close_date=None
        )
MOCK_PRODUCT = Product(
    name='MicroLoan',
    max_amount=30000,
    term_days=30,
    interest_rate_daily=1.2
)


@pytest.fixture
def clear_db():
    CLIENT_PROFILE_DB.clear()
    yield
    CLIENT_PROFILE_DB.clear()


@pytest.mark.asyncio
async def test_save_user_profile_success(clear_db):
    repo = ClientProfileRepository()

    await repo.save_user_profile(MOCK_USER_DATA)

    assert len(CLIENT_PROFILE_DB) == 1
    assert CLIENT_PROFILE_DB[MOCK_USER_DATA.phone].user_data == MOCK_USER_DATA


@pytest.mark.asyncio
async def test_save_user_credit_history(clear_db):
    repo = ClientProfileRepository()
    phone = MOCK_USER_DATA.phone
    await repo.save_user_profile(MOCK_USER_DATA)
    await repo.save_user_credit_history(phone, MOCK_PRODUCT)

    assert len(CLIENT_PROFILE_DB) == 1
    assert CLIENT_PROFILE_DB[MOCK_USER_DATA.phone].credit_history[0] == MOCK_CREDIT_ITEM
