from datetime import date

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: PhoneNumber
    birth_date: date


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
