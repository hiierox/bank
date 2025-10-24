from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.api.user_data.schemas import (
    GetUserProfileResponse,
    LoanEntryItem,
    LoanEntryUpdate,
    PutUserProfileRequest,
    UserProfile,
)
from app.core.custom_exceptions import (
    LoanAlreadyExistError,
    LoanNotFoundError,
    UserNotFoundError,
)
from app.logic.data_service import UserDataService
from app.repository.client_repo import ClientRepository

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

MOCK_PHONE = '79123456789'


@pytest.fixture
def user_data_service_fixture():
    mock_client_repo = AsyncMock(spec=ClientRepository)
    data_service = UserDataService(mock_client_repo)

    return mock_client_repo, data_service


@pytest.mark.asyncio
async def test_get_user_profile_success(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = {
        'profile': MOCK_USER_PROFILE,
        'history': [MOCK_LOAN_ENTRY]
    }

    result = await data_service.get_user_profile(MOCK_PHONE)

    assert isinstance(result, GetUserProfileResponse)
    assert result.phone == MOCK_PHONE
    assert result.profile == MOCK_USER_PROFILE
    assert result.history == [MOCK_LOAN_ENTRY]
    mock_client_repo.get_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_profile_not_found(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = None

    with pytest.raises(UserNotFoundError, match='User not found'):
        await data_service.get_user_profile(MOCK_PHONE)
    mock_client_repo.get_user_profile.assert_called_once()



@pytest.mark.asyncio
async def test_put_user_data_update_profile(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = {
        'profile': MOCK_USER_PROFILE,
        'history': []
    }
    mock_client_repo.update_or_create_user_profile.return_value = False
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=MOCK_USER_PROFILE, loan_entry=None)

    is_new = await data_service.put_user_data(MOCK_PHONE, request)

    assert is_new is False
    mock_client_repo.update_or_create_user_profile.assert_called_once()
    mock_client_repo.get_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_put_user_data_add_loan_entry(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = {
        'profile': MOCK_USER_PROFILE,
        'history': []
    }
    mock_client_repo.is_loan_entry_in_db.return_value = False
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=None, loan_entry=MOCK_LOAN_ENTRY)

    is_new = await data_service.put_user_data(MOCK_PHONE, request)

    assert is_new is False
    mock_client_repo.get_user_profile.assert_called_once()
    mock_client_repo.is_loan_entry_in_db.assert_called_once()
    mock_client_repo.add_new_loan_entry.assert_called_once()


@pytest.mark.asyncio
async def test_put_user_data_update_loan_entry(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = {
        'profile': MOCK_USER_PROFILE,
        'history': [MOCK_LOAN_ENTRY]
    }
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=None, loan_entry=MOCK_LOAN_UPDATE)

    is_new = await data_service.put_user_data(MOCK_PHONE, request)

    assert is_new is False
    mock_client_repo.get_user_profile.assert_called_once()
    mock_client_repo.update_loan_entry.assert_called_once()


@pytest.mark.asyncio
async def test_put_user_data_combined_update(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = True
    mock_client_repo.update_or_create_user_profile.return_value = True
    mock_client_repo.is_loan_entry_in_db.return_value = False
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=MOCK_USER_PROFILE, loan_entry=MOCK_LOAN_ENTRY)

    is_new = await data_service.put_user_data(MOCK_PHONE, request)

    assert is_new is True
    mock_client_repo.update_or_create_user_profile.assert_called_once()
    mock_client_repo.get_user_profile.assert_called_once()
    mock_client_repo.is_loan_entry_in_db.assert_called_once()
    mock_client_repo.add_new_loan_entry.assert_called_once()


@pytest.mark.asyncio
async def test_put_user_data_user_not_found_for_loan(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = None
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=None, loan_entry=MOCK_LOAN_ENTRY)

    with pytest.raises(UserNotFoundError, match='User not found'):
        await data_service.put_user_data(MOCK_PHONE, request)
    mock_client_repo.get_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_put_user_data_loan_already_exists(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = {
        'profile': MOCK_USER_PROFILE,
        'history': []
    }
    mock_client_repo.is_loan_entry_in_db.return_value = True
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=None, loan_entry=MOCK_LOAN_ENTRY)

    with pytest.raises(LoanAlreadyExistError):
        await data_service.put_user_data(MOCK_PHONE, request)
    mock_client_repo.get_user_profile.assert_called_once()
    mock_client_repo.is_loan_entry_in_db.assert_called_once()


@pytest.mark.asyncio
async def test_put_user_data_loan_not_found(user_data_service_fixture):
    mock_client_repo, data_service = user_data_service_fixture
    mock_client_repo.get_user_profile.return_value = {
        'profile': MOCK_USER_PROFILE,
        'history': []
    }
    mock_client_repo.update_loan_entry.side_effect = LoanNotFoundError
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=None, loan_entry=MOCK_LOAN_UPDATE)

    with pytest.raises(LoanNotFoundError):
        await data_service.put_user_data(MOCK_PHONE, request)
    mock_client_repo.get_user_profile.assert_called_once()
    mock_client_repo.update_loan_entry.assert_called_once()
