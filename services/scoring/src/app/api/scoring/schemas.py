import re

from pydantic import BaseModel, field_validator


class UserData(BaseModel):
    phone: str
    age: int
    monthly_income: int
    employment_type: str
    has_property: bool

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not re.fullmatch(r'^7\d{10}$', value):
            raise ValueError('Wrong number format')
        return value

    @field_validator('monthly_income')
    @classmethod
    def convert_income_to_kops(cls, value: int) -> int:
        return value * 100


class Product(BaseModel):
    name: str
    max_amount: int
    term_days: int
    interest_rate_daily: float


class ScoringRequest(BaseModel):
    user_data: UserData
    products: list[Product]


class ResponseModel(BaseModel):
    decision: str
    product: Product | None

