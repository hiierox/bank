from datetime import date
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

PHONE_REG = r'^7\d{10}$'


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    age: int = Field(..., ge=0, le=120)
    monthly_income: int = Field(..., gt=0)
    employment_type: Literal['full_time', 'freelance']
    has_property: bool


class LoanEntryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    loan_id: str
    product_name: str
    amount: int = Field(..., gt=0)
    issue_date: date
    term_days: int = Field(..., gt=0)
    status: str
    close_date: date | None = None

    @model_validator(mode='after')
    def validate_status_close_date_relation(self) -> Self:
        if self.status == 'open' and self.close_date is not None:
            raise ValueError('Close date cant exist if status is open')
        if self.status == 'closed' and self.close_date is None:
            raise ValueError('Close date is required for closed status')
        return self


class LoanEntryUpdate(BaseModel):
    loan_id: str
    status: str
    close_date: date | None

    @model_validator(mode='after')
    def validate_status_close_date_relation(self) -> Self:
        if self.status == 'open' and self.close_date is not None:
            raise ValueError('Close date cant exist if status is open')
        if self.status == 'closed' and self.close_date is None:
            raise ValueError('Close date is required for closed status')
        return self


class GetUserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    profile: UserProfile
    history: list[LoanEntryItem] = []


class PutUserProfileRequest(BaseModel):
    phone: str = Field(pattern=PHONE_REG, min_length=11, max_length=11)
    profile: UserProfile | None = None
    loan_entry: LoanEntryItem | LoanEntryUpdate | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_name: str
    amount: int
    percentage: float
