from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

PHONE_REG = r'^7\d{10}$'


class UserData(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    age: int = Field(..., ge=0, le=120)
    monthly_income: int = Field(..., ge=0)
    employment_type: Literal['full_time', 'freelance', 'unemployed']
    has_property: bool

    @field_validator('monthly_income')
    @classmethod
    def convert_income_to_kops(cls, value: int) -> int:
        return value * 100


class UserDataFromDataService(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    age: int = Field(..., ge=0, le=120)
    monthly_income: int = Field(..., ge=0)
    employment_type: Literal['full_time', 'freelance', 'unemployed']
    has_property: bool


class Product(BaseModel):
    name: str
    max_amount: int = Field(..., gt=0)
    term_days: int = Field(..., gt=0)
    interest_rate_daily: float


class ScoringRequestPioneer(BaseModel):
    user_data: UserData
    products: list[Product]


class ScoringRequestRepeater(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    products: list[Product]


class ResponseModel(BaseModel):
    decision: str
    product: Product | None


class CreditHistoryItem(BaseModel):
    loan_id: str
    product_name: str
    amount: int
    issue_date: date
    term_days: int
    status: str
    close_date: date | None = None


class UserProfileForDataService(BaseModel):
    age: int = Field(..., ge=0, le=120)
    monthly_income: int = Field(..., gt=0)
    employment_type: Literal['full_time', 'freelance', 'unemployed']
    has_property: bool

class PutUserData(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    profile: UserProfileForDataService | None = None
    loan_entry: CreditHistoryItem


class GetUserProfileResponse(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    profile: UserProfileForDataService
    history: list[CreditHistoryItem] = []


class AntifraudCheckResponse(BaseModel):
    decision: Literal['passed', 'rejected']
    reasons: list[str]
