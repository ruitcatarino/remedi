from pydantic import BaseModel, EmailStr
from datetime import date


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: str
    birth_date: date
