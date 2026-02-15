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


@pytest.mark.parametrize(
        ('age', 'expected_reason'),
        [
            (B1_MIN_AGE + 1, None),
            (B1_MIN_AGE - 1, REJECT_REASON_B1)
        ],
        ids=('acceptable age', 'Too young age')
)
def test_check_min_age_boundary_values(age, expected_reason):
    """B1: Граничные значения возраста."""
    result = CommonChecks.check_min_age(age)
    assert result == expected_reason


@pytest.mark.parametrize(
        ('monthly_income', 'expected_reason'),
        [
            (B2_MIN_INCOME + 1, None),
            (B2_MIN_INCOME - 1, REJECT_REASON_B2)
        ],
        ids=('Enough income', 'Low income')
)
def test_check_min_income_boundary_values(monthly_income, expected_reason):
    """B2: Граничные значения дохода."""
    result = CommonChecks.check_min_income(monthly_income)
    assert result == expected_reason


@pytest.mark.parametrize(
        ('employment_status', 'expected_reason'),
        [
            ('full_time', None),
            ('unemployed', REJECT_REASON_B3)
        ],
        ids=('full_time', 'unemployed')
)
def test_check_employment_status(employment_status, expected_reason):
    """B3: Проверка занятости."""
    result = CommonChecks.check_employment_status(employment_status)
    assert result == expected_reason


def test_common_checks_run_happy_path():
    """CommonChecks.run возвращает пустой список при успехе."""
    profile = UserProfileData(
        phone='71112223334',
        age=B1_MIN_AGE + 5,
        monthly_income=B2_MIN_INCOME + 5000,
        employment_type='full_time',
        has_property=True,
    )

    reasons = CommonChecks.run(profile)
    
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
