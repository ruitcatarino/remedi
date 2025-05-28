from datetime import date

from pydantic import BaseModel


class PersonSchema(BaseModel):
    id: int
    name: str
    birth_date: date | None = None
    notes: str | None = None


class PersonRegisterSchema(BaseModel):
    name: str
    birth_date: date | None = None
    notes: str | None = None


class PersonUpdateSchema(BaseModel):
    name: str | None = None
    birth_date: date | None = None
    notes: str | None = None
