from datetime import date

import pytest

from app.api.user_data.schemas import LoanEntryItem, LoanEntryUpdate, UserProfile
from app.core.custom_exceptions import LoanNotFoundError, UserNotFoundError
from app.repository.client_repo import USER_PROFILE_DB, ClientRepository

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
def clear_db():
    USER_PROFILE_DB.clear()
    yield
    USER_PROFILE_DB.clear()


@pytest.mark.asyncio
async def test_get_user_profile_success(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': []}

    result = await repo.get_user_profile(phone)

    assert result is not None
    assert result['profile'] == MOCK_USER_PROFILE
    assert result['history'] == []


@pytest.mark.asyncio
async def test_get_user_profile_non_existing(clear_db):
    repo = ClientRepository()
    phone = '79999999999'

    result = await repo.get_user_profile(phone)

    assert result is None


@pytest.mark.asyncio
async def test_is_loan_entry_in_db_true(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': [MOCK_LOAN_ENTRY]}

    result = await repo.is_loan_entry_in_db(phone, MOCK_LOAN_ENTRY.loan_id)

    assert result is True


@pytest.mark.asyncio
async def test_is_loan_entry_in_db_non_existing(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': []}

    result = await repo.is_loan_entry_in_db(phone, MOCK_LOAN_ENTRY.loan_id)

    assert result is False


@pytest.mark.asyncio
async def test_is_loan_entry_in_db_user_not_found(clear_db):
    repo = ClientRepository()
    phone = '79999999999'

    with pytest.raises(UserNotFoundError):
        await repo.is_loan_entry_in_db(phone, MOCK_LOAN_ENTRY.loan_id)


@pytest.mark.asyncio
async def test_update_or_create_user_profile_create(clear_db):
    repo = ClientRepository()
    phone = '79123456789'

    is_new = await repo.update_or_create_user_profile(phone, MOCK_USER_PROFILE)

    assert is_new is True
    assert len(USER_PROFILE_DB) == 1
    assert USER_PROFILE_DB[phone]['profile'] == MOCK_USER_PROFILE
    assert USER_PROFILE_DB[phone]['history'] == []


@pytest.mark.asyncio
async def test_update_or_create_user_profile_update(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': []}
    new_profile = UserProfile(
        age=31,
        monthly_income=60000,
        employment_type='freelance',
        has_property=False
    )

    is_new = await repo.update_or_create_user_profile(phone, new_profile)

    assert is_new is False
    assert len(USER_PROFILE_DB) == 1
    assert USER_PROFILE_DB[phone]['profile'] == new_profile
    assert USER_PROFILE_DB[phone]['history'] == []


@pytest.mark.asyncio
async def test_add_new_loan_entry_success(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': []}

    await repo.add_new_loan_entry(phone, MOCK_LOAN_ENTRY)

    assert len(USER_PROFILE_DB[phone]['history']) == 1
    assert USER_PROFILE_DB[phone]['history'][0] == MOCK_LOAN_ENTRY


@pytest.mark.asyncio
async def test_add_new_loan_entry_user_not_found(clear_db):
    repo = ClientRepository()
    phone = '79999999999'

    with pytest.raises(UserNotFoundError):
        await repo.add_new_loan_entry(phone, MOCK_LOAN_ENTRY)


@pytest.mark.asyncio
async def test_update_loan_entry_success(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': [MOCK_LOAN_ENTRY]}

    await repo.update_loan_entry(phone, MOCK_LOAN_UPDATE)

    updated_loan = USER_PROFILE_DB[phone]['history'][0]
    assert updated_loan.status == MOCK_LOAN_UPDATE.status
    assert updated_loan.close_date == MOCK_LOAN_UPDATE.close_date
    assert updated_loan.product_name == MOCK_LOAN_ENTRY.product_name


@pytest.mark.asyncio
async def test_update_loan_entry_user_not_found(clear_db):
    repo = ClientRepository()
    phone = '79999999999'

    with pytest.raises(UserNotFoundError):
        await repo.update_loan_entry(phone, MOCK_LOAN_UPDATE)


@pytest.mark.asyncio
async def test_update_loan_entry_loan_not_found(clear_db):
    repo = ClientRepository()
    phone = '79123456789'
    USER_PROFILE_DB[phone] = {'profile': MOCK_USER_PROFILE, 'history': []}

    with pytest.raises(LoanNotFoundError):
        await repo.update_loan_entry(phone, MOCK_LOAN_UPDATE)
