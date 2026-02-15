from typing import Literal

from pydantic import BaseModel, Field

from app.api.antifraud.schemas import LoanItem

PHONE_REG = r'^7\d{10}$'


class UserProfileFromDataService(BaseModel):
    """Схема профиля пользователя,полученного из БД"""
    age: int = Field(..., ge=0, le=120)
    monthly_income: int = Field(..., gt=0)
    employment_type: Literal['full_time', 'freelance', 'unemployed']
    has_property: bool


class UserDataFromDataServiceResponse(BaseModel):
    """ответ от data-service"""
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    profile: UserProfileFromDataService
    history: list[LoanItem] = []
