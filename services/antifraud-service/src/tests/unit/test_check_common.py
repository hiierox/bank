import pytest

from app.api.antifraud.schemas import UserProfileData
from app.core.constants import (
    B1_MIN_AGE,
    B2_MIN_INCOME,
    REJECT_REASON_B1,
    REJECT_REASON_B2,
    REJECT_REASON_B3,
)
from app.logic.check_rules import CommonChecks


@pytest.fixture
def mock_profile_data():
    """Профиль, который должен пройти все CommonChecks."""
    return UserProfileData(
        phone='71112223334',
        age=B1_MIN_AGE + 5,
        monthly_income=B2_MIN_INCOME + 5000,
        employment_type='full_time',
        has_property=True,
    )


def test_check_min_age_passed(mock_profile_data):
    """B1: Возраст выше минимального."""
    result = CommonChecks.check_min_age(mock_profile_data.age)
    assert result is None

def test_check_min_age_rejected_boundary():
    """B1: Возраст на 1 год меньше минимума"""
    result = CommonChecks.check_min_age(B1_MIN_AGE - 1)
    assert result == REJECT_REASON_B1


def test_check_min_income_passed(mock_profile_data):
    """B2: Доход выше минимального."""
    result = CommonChecks.check_min_income(mock_profile_data.monthly_income)
    assert result is None

def test_check_min_income_rejected_boundary():
    """B2: Доход на 1 меньше минимума."""
    result = CommonChecks.check_min_income(B2_MIN_INCOME - 1)
    assert result == REJECT_REASON_B2


def test_check_employment_status_passed():
    """B3: Статус full_time подходит."""
    result = CommonChecks.check_employment_status('full_time')
    assert result is None

def test_check_employment_status_rejected():
    """B3: Статус unemployed не подходит."""
    result = CommonChecks.check_employment_status('unemployed')
    assert result == REJECT_REASON_B3


def test_common_checks_run_happy_path(mock_profile_data):
    """CommonChecks.run возвращает пустой список при успехе."""
    reasons = CommonChecks.run(mock_profile_data)
    assert reasons == []

def test_common_checks_run_multiple_rejected():
    """CommonChecks.run возвращает несколько причин отказа."""
    rejected_profile = UserProfileData(
        phone='71231231230',
        age=10,
        monthly_income=B2_MIN_INCOME + 1,
        employment_type='unemployed',
        has_property=False,
    )
    reasons = CommonChecks.run(rejected_profile)

    expected_reasons = [REJECT_REASON_B1, REJECT_REASON_B3]
    assert reasons == expected_reasons
