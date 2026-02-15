from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.user_data.schemas import (
    GetUserProfileResponse,
    LoanEntryItem,
    LoanEntryUpdate,
    PutUserProfileRequest,
    UserProfile,
)
from app.core.custom_exceptions import LoanAlreadyExistError, UserNotFoundError
from app.database.models import Loan, User
from app.logic.data_service import UserDataService

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
async def fixture():
    with patch('app.logic.data_service.UserRepository', autospec=True) as MockUserRepo, \
            patch('app.logic.data_service.LoanRepository', autospec=True) as MockLoanRepo:

        yield MockUserRepo, MockLoanRepo


@pytest.mark.asyncio
async def test_get_user_profile_success(fixture):
    """Успешный поиск пользователя"""
    MockUserRepo, _ = fixture
    user_from_db = User(
        phone='79123456789',
        age=30,
        monthly_income=100000,
        employment_type='full_time',
        has_property=True,
        loans=[
            Loan(loan_id='loan_20250115_001',
                 product_name='LoyaltyLoan',
                 amount=50000,
                 issue_date=date(2025, 1, 15),
                 term_days=90,
                 status='open',
                 close_date=None)
        ]
    )

    mock_repo_instance = AsyncMock()
    mock_repo_instance.get_user_profile.return_value = user_from_db
    MockUserRepo.return_value = mock_repo_instance
    service = UserDataService(session=AsyncMock())

    result = await service.get_user_profile(phone=MOCK_PHONE)

    mock_repo_instance.get_user_profile.assert_awaited_once_with(
            MOCK_PHONE)
    assert isinstance(result, GetUserProfileResponse)
    assert result.phone == MOCK_PHONE
    assert result.profile.age == MOCK_USER_PROFILE.age
    assert len(result.history) == 1
    assert result.history[0].loan_id == MOCK_LOAN_ENTRY.loan_id


@pytest.mark.asyncio
async def test_get_user_profile_not_found(fixture):
    """Выбрасывается исключение UserNotFoundError, если пользователь не найден."""
    MockUserRepo, _ = fixture
    mock_repo_instance = AsyncMock()
    mock_repo_instance.get_user_profile.return_value = None
    MockUserRepo.return_value = mock_repo_instance

    service = UserDataService(session=AsyncMock())
    with pytest.raises(UserNotFoundError):
        await service.get_user_profile(phone=MOCK_PHONE)
    mock_repo_instance.get_user_profile.assert_awaited_once_with(
            MOCK_PHONE)


@pytest.mark.asyncio
async def test_put_user_data_creates_new_user_and_loan(fixture):
    """Создается новый пользователь и добавляется новый кредит."""
    MockUserRepo, MockLoanRepo = fixture

    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=MOCK_USER_PROFILE, loan_entry=MOCK_LOAN_ENTRY)

    MockUserRepo.return_value.update_or_create_user_profile.return_value = True
    MockUserRepo.return_value.get_user_profile.return_value = User(
        phone=MOCK_PHONE)
    MockLoanRepo.return_value.is_loan_entry_in_db.return_value = False

    service = UserDataService(session=MagicMock())
    is_new_user = await service.put_user_data(MOCK_PHONE, request)

    assert is_new_user is True
    MockUserRepo.return_value.update_or_create_user_profile.assert_awaited_once()
    MockLoanRepo.return_value.is_loan_entry_in_db.assert_awaited_once_with(
        MOCK_LOAN_ENTRY.loan_id)
    MockLoanRepo.return_value.add_new_loan_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_put_user_data_updates_user_and_adds_loan(fixture):
    """Обновляется существующий пользователь и добавляется новый кредит."""
    MockUserRepo, MockLoanRepo = fixture
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, profile=MOCK_USER_PROFILE, loan_entry=MOCK_LOAN_ENTRY)

    MockUserRepo.return_value.update_or_create_user_profile.return_value = False
    MockUserRepo.return_value.get_user_profile.return_value = User(
        phone=MOCK_PHONE)
    MockLoanRepo.return_value.is_loan_entry_in_db.return_value = False

    service = UserDataService(session=MagicMock())
    is_new_user = await service.put_user_data(MOCK_PHONE, request)

    assert is_new_user is False
    MockUserRepo.return_value.update_or_create_user_profile.assert_awaited_once()
    MockLoanRepo.return_value.add_new_loan_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_put_user_data_updates_existing_loan(fixture):
    """Обновляется статус существующего кредита без изменения профиля"""
    MockUserRepo, MockLoanRepo = fixture
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, loan_entry=MOCK_LOAN_UPDATE)

    MockUserRepo.return_value.get_user_profile.return_value = User(
        phone=MOCK_PHONE)

    service = UserDataService(session=MagicMock())
    await service.put_user_data(MOCK_PHONE, request)

    MockUserRepo.return_value.update_or_create_user_profile.assert_not_called()
    MockLoanRepo.return_value.add_new_loan_entry.assert_not_called()
    MockLoanRepo.return_value.update_loan_entry.assert_awaited_once_with(
        loan_id=MOCK_LOAN_UPDATE.loan_id,
        status=MOCK_LOAN_UPDATE.status,
        close_date=MOCK_LOAN_UPDATE.close_date
    )


@pytest.mark.asyncio
async def test_put_user_data_fails_if_loan_already_exists(fixture):
    """Выбрасывается исключение LoanAlreadyExistError
    при попытке добавить существующий кредит
    """
    MockUserRepo, MockLoanRepo = fixture
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, loan_entry=MOCK_LOAN_ENTRY)

    MockUserRepo.return_value.get_user_profile.return_value = User(
        phone=MOCK_PHONE)
    MockLoanRepo.return_value.is_loan_entry_in_db.return_value = True

    service = UserDataService(session=MagicMock())
    with pytest.raises(LoanAlreadyExistError):
        await service.put_user_data(MOCK_PHONE, request)


@pytest.mark.asyncio
async def test_put_user_data_fails_if_user_not_found_for_loan_addition(fixture):
    """Выбрасывается UserNotFoundError,
    если добавляем кредит несуществующему пользователю
    """
    MockUserRepo, MockLoanRepo = fixture
    request = PutUserProfileRequest(
        phone=MOCK_PHONE, loan_entry=MOCK_LOAN_ENTRY)

    MockUserRepo.return_value.get_user_profile.return_value = None

    service = UserDataService(session=MagicMock())
    with pytest.raises(UserNotFoundError):
        await service.put_user_data(MOCK_PHONE, request)
    MockLoanRepo.return_value.is_loan_entry_in_db.assert_not_called()
