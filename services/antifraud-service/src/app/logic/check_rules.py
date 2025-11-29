import logging
from datetime import date, timedelta

from app.api.antifraud.schemas import (
    DataServiceResponse,
    LoanItem,
    UserProfileData,
)
from app.core.constants import (
    B1_MIN_AGE,
    B2_MIN_INCOME,
    B3_DISALLOWED_EMPLOYMENT_TYPES,
    P1_MAX_APPLICATIONS,
    P2_MIN_INCOME_WITH_PROPERTY,
    R2_INCOME_FALL_FACTOR,
    R2_INCOME_GROWTH_FACTOR,
    R2_PROFILE_CHECK_DAYS,
    REJECT_REASON_B1,
    REJECT_REASON_B2,
    REJECT_REASON_B3,
    REJECT_REASON_P1,
    REJECT_REASON_P2,
    REJECT_REASON_R1,
    REJECT_REASON_R2_EMPLOYMENT_CHANGE,
    REJECT_REASON_R2_INCOME_FALL,
    REJECT_REASON_R2_INCOME_GROWTH,
)

logger = logging.getLogger(__name__)


class CommonChecks:
    """Общие для любого флоу антифрод проверки (B1, B2, B3)."""

    @staticmethod
    def check_min_age(age: int) -> str | None:
        """B1: age >= 18."""
        if age < B1_MIN_AGE:
            return REJECT_REASON_B1
        return None

    @staticmethod
    def check_min_income(income: int) -> str | None:
        """B2: monthly_income >= 10000."""
        if income < B2_MIN_INCOME:
            return REJECT_REASON_B2
        return None

    @staticmethod
    def check_employment_status(employment_type: str) -> str | None:
        """B3: employment_type != "unemployed"."""
        if employment_type in B3_DISALLOWED_EMPLOYMENT_TYPES:
            return REJECT_REASON_B3
        return None

    @classmethod
    def run(cls, profile: UserProfileData) -> list[str]:
        """
        Запускает все общие проверки для заданного профиля.
        Вернет список причин отказа (пустой, если все проверки пройдены).
        """
        reasons = [
            cls.check_min_age(profile.age),
            cls.check_min_income(profile.monthly_income),
            cls.check_employment_status(profile.employment_type),
        ]

        return [r for r in reasons if r is not None]


class PioneerChecks:
    """Антифрод проверки для pioneer (P1, P2)."""

    @staticmethod
    def check_daily_application_limit(application_count: int) -> str | None:
        """P1: > 3 заявок -> отказ."""
        if application_count >= P1_MAX_APPLICATIONS:
            return REJECT_REASON_P1
        return None

    @staticmethod
    def check_property_low_income(
        has_property: bool, monthly_income: int
    ) -> str | None:
        """P2: has_property=true и monthly_income < 30000 -> отказ."""
        if has_property and monthly_income < P2_MIN_INCOME_WITH_PROPERTY:
            return REJECT_REASON_P2
        return None

    @classmethod
    def run(
        cls,
        user_data: UserProfileData,
        application_count: int,
    ) -> list[str]:
        """
        Запускает все pioneer проверки.
        Вернет список причин отказа (пустой, если все проверки пройдены).
        """
        reasons = [
            cls.check_daily_application_limit(application_count),
            cls.check_property_low_income(
                user_data.has_property, user_data.monthly_income
            ),
        ]
        return [r for r in reasons if r is not None]


class RepeaterChecks:
    """антифрод проверки для repeater (R1, R2)."""

    @staticmethod
    def check_overdue_payments(history: list[LoanItem]) -> str | None:
        """R1: Если есть хотя бы один займ co статусом "overdue" -> отказ."""
        for loan in history:
            if loan.status == 'overdue':
                return REJECT_REASON_R1
        return None

    @staticmethod
    def _is_recent_loan(
        last_loan_issue_date: date, check_date: date) -> bool:
        """
        Проверяет, что разница между датой заявки и
        датой последнего кредита <= 30 дней.
        """
        return (
            (check_date - last_loan_issue_date) <= timedelta(days=R2_PROFILE_CHECK_DAYS)
        )

    @staticmethod
    def check_income_change(
        current_income: int,
        past_income: int,
    ) -> str | None:
        """R2: Проверка на резкое изменение дохода (+100% или -50%)."""

        if current_income >= R2_INCOME_GROWTH_FACTOR * past_income:
            return REJECT_REASON_R2_INCOME_GROWTH

        if current_income <= R2_INCOME_FALL_FACTOR * past_income:
            return REJECT_REASON_R2_INCOME_FALL

        return None

    @staticmethod
    def check_employment_change(
        current_employment: str,
        past_employment: str,
    ) -> str | None:
        """
        R2: Проверка на изменение employment_type c full_time на freelance, unemployed
        """
        if past_employment == 'full_time' and current_employment != 'full_time':
            return REJECT_REASON_R2_EMPLOYMENT_CHANGE
        return None

    @classmethod
    def run(
        cls,
        new_updated_profile: UserProfileData,
        data_service_response: DataServiceResponse,
        check_date: date
    ) -> list[str]:
        """
        Запускает все repeater проверки
        Вернет список причин отказа (пустой, если все проверки пройдены).
        """
        reasons = []

        reasons.append(cls.check_overdue_payments(data_service_response.history))

        profile_data = data_service_response.profile
        loan_data = data_service_response.history

        if profile_data is not None and cls._is_recent_loan(
            loan_data[-1].issue_date, check_date
        ):
            reasons.append(
                cls.check_income_change(
                    new_updated_profile.monthly_income, profile_data.monthly_income
                )
            )

            reasons.append(
                cls.check_employment_change(
                    new_updated_profile.employment_type, profile_data.employment_type
                )
            )

        return [r for r in reasons if r is not None]
