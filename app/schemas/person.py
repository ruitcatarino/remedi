from datetime import date

from pydantic import BaseModel


class PersonSchema(BaseModel):
    name: str
    birth_date: date | None = None
    notes: str | None = None


class PersonFullSchema(BaseModel):
    id: int
    name: str
    birth_date: date | None = None
    notes: str | None = None
