from datetime import date

from pydantic import BaseModel, Field, field_validator

PHONE_REG = r'^7\d{10}$'


class UserData(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    age: int
    monthly_income: int
    employment_type: str
    has_property: bool

    @field_validator('monthly_income')
    @classmethod
    def convert_income_to_kops(cls, value: int) -> int:
        return value * 100


class Product(BaseModel):
    name: str
    max_amount: int
    term_days: int
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
    product_name: str
    amount: int
    issue_date: date
    term_days: int
    status: str
    close_date: date | None = None


class ClientProfile(BaseModel):
    user_data: UserData
    credit_history: list[CreditHistoryItem] = []
