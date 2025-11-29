import pytest

from app.api.antifraud.schemas import UserProfileData
from app.core.constants import (
    P1_MAX_APPLICATIONS,
    P2_MIN_INCOME_WITH_PROPERTY,
    REJECT_REASON_P1,
    REJECT_REASON_P2,
)
from app.logic.check_rules import PioneerChecks


@pytest.fixture
def mock_pioneer_data():
    """Профиль, который должен пройти все PioneerChecks"""
    return UserProfileData(
        phone='71112223334',
        age=30,
        monthly_income=P2_MIN_INCOME_WITH_PROPERTY + 1,
        employment_type='full_time',
        has_property=True,
    )


def test_check_app_limit_passed_zero_count():
    """P1: 0 заявок, проходит."""
    result = PioneerChecks.check_daily_application_limit(0)
    assert result is None


def test_check_app_limit_passed_boundary_pass():
    """P1: Количество заявок, которое еще позволяет пройти."""
    result = PioneerChecks.check_daily_application_limit(P1_MAX_APPLICATIONS - 1)
    assert result is None


def test_check_app_limit_rejected_boundary():
    """P1: Количество заявок, которое ровно лимиту"""
    result = PioneerChecks.check_daily_application_limit(P1_MAX_APPLICATIONS)
    assert result == REJECT_REASON_P1


def test_check_app_limit_rejected_over_limit():
    """P1: Количество заявок, превышающее лимит."""
    result = PioneerChecks.check_daily_application_limit(P1_MAX_APPLICATIONS + 1)
    assert result == REJECT_REASON_P1


def test_check_property_low_income_passed_high_income(mock_pioneer_data):
    """P2: Есть недвижимость и высокий доход"""
    result = PioneerChecks.check_property_low_income(
        has_property=True, monthly_income=mock_pioneer_data.monthly_income
    )
    assert result is None


def test_check_property_low_income_passed_no_property():
    """P2: Нет недвижимости и низкий доход"""
    result = PioneerChecks.check_property_low_income(
        has_property=False, monthly_income=P2_MIN_INCOME_WITH_PROPERTY - 1000
    )
    assert result is None


def test_check_property_low_income_rejected_boundary():
    """P2: Есть недвижимость, доход на 1 меньше лимита."""
    result = PioneerChecks.check_property_low_income(
        has_property=True, monthly_income=P2_MIN_INCOME_WITH_PROPERTY - 1
    )
    assert result == REJECT_REASON_P2


def test_pioneer_checks_run_happy_path(mock_pioneer_data):
    """run возвращает пустой список при успехе."""
    reasons = PioneerChecks.run(
        user_data=mock_pioneer_data,
        application_count=P1_MAX_APPLICATIONS - 1,
    )
    assert reasons == []


def test_pioneer_checks_run_both_rejected(mock_pioneer_data):
    """run возвращает две сработавшие причины P1 и P2."""
    app_count = P1_MAX_APPLICATIONS

    rejected_data = mock_pioneer_data.model_copy(
        update={
            'has_property': True,
            'monthly_income': P2_MIN_INCOME_WITH_PROPERTY - 1000,
        }
    )

    reasons = PioneerChecks.run(user_data=rejected_data, application_count=app_count)

    expected_reasons = [REJECT_REASON_P1, REJECT_REASON_P2]
    assert reasons == expected_reasons
