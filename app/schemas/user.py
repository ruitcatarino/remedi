from datetime import date

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: str
    birth_date: date


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
