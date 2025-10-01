from pydantic import BaseModel, validator


class NumberRequest(BaseModel):
    phone_number: str

    @validator("phone_number")
    def validate_phone_number(cls, value):
        if not value.isdigit() or len(value) != 11 or value[0] != "7":
            raise ValueError("Wrong number format")
        return value


class Product(BaseModel):
    name: str
    amount: str
    percentage: str


class ResponseModel(BaseModel):
    flow_type: str
    available_products: list[Product] = []