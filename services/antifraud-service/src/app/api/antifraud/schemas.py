from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

PHONE_REG = r'^7\d{10}$'


class UserProfileData(BaseModel):
    """Схема для входных данных профиля"""
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    age: int = Field(..., ge=0, le=120)
    monthly_income: int = Field(..., ge=0)
    employment_type: Literal['full_time', 'freelance', 'unemployed']
    has_property: bool


class PioneerCheckRequest(BaseModel):
    """/api/antifraud/pioneer/check"""
    user_data: UserProfileData


class RepeaterCheckRequest(BaseModel):
    """/api/antifraud/repeater/check"""
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    new_updated_profile: UserProfileData


class LoanItem(BaseModel):
    """Данные o конкретном кредите"""
    loan_id: str
    product_name: str
    amount: int
    issue_date: date
    term_days: int
    status: str
    close_date: date | None = None


class AnfifraudDecision(str, Enum):
    """Возможные решения антифрод-сервиса."""
    PASSED = 'passed'
    REJECTED = 'rejected'


class AntifraudDecisionResponse(BaseModel):
    """Финальный ответ от антифрод-сервиса"""
    decision: AnfifraudDecision
    reasons: list[str]
