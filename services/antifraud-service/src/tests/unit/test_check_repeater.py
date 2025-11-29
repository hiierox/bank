from datetime import date, timedelta

import pytest

from app.api.antifraud.schemas import (
    DataServiceResponse,
    LoanItem,
    UserProfileData,
    UserProfileFromDataService,
)
from app.core.constants import (
    R2_PROFILE_CHECK_DAYS,
    REJECT_REASON_R1,
    REJECT_REASON_R2_EMPLOYMENT_CHANGE,
    REJECT_REASON_R2_INCOME_FALL,
    REJECT_REASON_R2_INCOME_GROWTH,
)
from app.logic.check_rules import RepeaterChecks

TODAY = date(2025, 12, 1)


@pytest.fixture
def mock_clean_history():
    return [
        LoanItem(
            loan_id='id1',
            product_name='Quick',
            amount=10000,
            issue_date=date(2025, 11, 20),
            term_days=30,
            status='closed',
            close_date=date(2025, 11, 25),
        ),
        LoanItem(
            loan_id='id2',
            product_name='Quick',
            amount=5000,
            issue_date=date(2025, 11, 29),
            term_days=30,
            status='open',
            close_date=None,
        ),
    ]


@pytest.fixture
def mock_past_profile():
    """Профиль из базы (c которым сравниваем)."""
    return UserProfileData(
        phone='79001234567',
        age=30,
        monthly_income=50000,
        employment_type='full_time',
        has_property=False,
    )


@pytest.fixture
def mock_data_service_response(mock_clean_history):
    """Ответ data-service для прохождения всех RepeaterChecks."""
    return DataServiceResponse(
        phone='79001234567',
        profile=UserProfileFromDataService(
            age=30,
            monthly_income=50000,
            employment_type='full_time',
            has_property=False,
        ),
        history=mock_clean_history,
    )


def test_check_overdue_payments_passed(mock_clean_history):
    """R1: Нет overdue статуса."""
    result = RepeaterChecks.check_overdue_payments(mock_clean_history)
    assert result is None


def test_check_overdue_payments_rejected():
    """R1: Есть overdue статус."""
    history_with_overdue = [
        LoanItem(
            loan_id='id3',
            product_name='Quick',
            amount=100,
            issue_date=date(2025, 10, 1),
            term_days=10,
            status='overdue',
            close_date=None,
        )
    ]
    result = RepeaterChecks.check_overdue_payments(history_with_overdue)
    assert result == REJECT_REASON_R1


def test_is_recent_loan_passed_boundary():
    """Кредит был взят ровно 30 дней назад."""
    issue_date = TODAY - timedelta(days=R2_PROFILE_CHECK_DAYS)
    assert RepeaterChecks._is_recent_loan(issue_date, TODAY) is True


def test_is_recent_loan_rejected_boundary():
    """Кредит был взят 31 день назад."""
    issue_date = TODAY - timedelta(days=R2_PROFILE_CHECK_DAYS + 1)
    assert RepeaterChecks._is_recent_loan(issue_date, TODAY) is False


@pytest.mark.parametrize(
    ('current_income', 'expected_reason'),
    [
        (100000, REJECT_REASON_R2_INCOME_GROWTH),
        (99999, None),
        (25001, None),
        (24999, REJECT_REASON_R2_INCOME_FALL),
        (50000, None),
    ],
)
def test_check_income_change_r2(mock_past_profile, current_income, expected_reason):
    """R2: Изменение дохода."""
    result = RepeaterChecks.check_income_change(
        current_income=current_income,
        past_income=mock_past_profile.monthly_income,
    )
    assert result == expected_reason


@pytest.mark.parametrize(
    ('past_employment', 'current_employment', 'expected_reason'),
    [
        ('full_time', 'freelance', REJECT_REASON_R2_EMPLOYMENT_CHANGE),
        ('full_time', 'unemployed', REJECT_REASON_R2_EMPLOYMENT_CHANGE),
        ('full_time', 'full_time', None),
        ('freelance', 'unemployed', None),
        ('unemployed', 'full_time', None),
    ],
)
def test_check_employment_change_r2(
    past_employment, current_employment, expected_reason
):
    """R2: Изменение типа занятости."""
    result = RepeaterChecks.check_employment_change(
        current_employment=current_employment, past_employment=past_employment
    )
    assert result == expected_reason


def test_repeater_checks_run_rejected_all(mock_data_service_response):
    """Проверка, что run возвращает R1, R2_Income, R2_Employment."""

    history_with_overdue = [
        LoanItem(
            loan_id='id3',
            product_name='Quick',
            amount=100,
            issue_date=date(2025, 11, 29),
            term_days=10,
            status='overdue',
            close_date=None,
        )
    ]

    rejected_profile = mock_data_service_response.model_copy(
        update={
            'monthly_income': 100000,
            'employment_type': 'freelance',
        }
    )

    response_for_rejected = DataServiceResponse(
        phone='79001234567',
        profile=UserProfileFromDataService(
            age=30,
            monthly_income=50000,
            employment_type='full_time',
            has_property=False,
        ),
        history=history_with_overdue,
    )

    reasons = RepeaterChecks.run(
        new_updated_profile=rejected_profile,
        data_service_response=response_for_rejected,
        check_date=TODAY,
    )

    expected_reasons = [
        REJECT_REASON_R1,
        REJECT_REASON_R2_INCOME_GROWTH,
        REJECT_REASON_R2_EMPLOYMENT_CHANGE,
    ]

    assert sorted(reasons) == sorted(expected_reasons)
