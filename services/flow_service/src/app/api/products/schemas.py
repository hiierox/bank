import re

from pydantic import BaseModel, field_validator


class NumberRequest(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.fullmatch(r'^7\d{10}$', value):
            raise ValueError('Wrong number format')
        return value


class Product(BaseModel):
    name: str
    amount: str
    percentage: str


class ResponseModel(BaseModel):
    flow_type: str
    available_products: list[Product] = []
