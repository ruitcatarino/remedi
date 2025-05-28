from datetime import date, timedelta
from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, model_validator

from app.schemas.person import PersonSchema


def convert_minutes_to_timedelta(value: int) -> timedelta:
    """Converts a frequency in minutes to a timedelta object."""
    if isinstance(value, int):
        return timedelta(minutes=value)
    raise ValueError("Frequency must be an integer (minutes)")


def convert_timedelta_to_minutes(value: timedelta) -> int:
    """Converts a timedelta object to a frequency in minutes."""
    return value.total_seconds() // 60


class MedicationSchema(BaseModel):
    id: int
    person: PersonSchema
    name: str
    dosage: str
    frequency: Annotated[int, BeforeValidator(convert_timedelta_to_minutes)]
    start_date: date
    end_date: date | None = None
    total_doses: int | None = None
    notes: str | None = None


class MedicationRegisterSchema(BaseModel):
    name: str
    person_id: int
    dosage: str
    frequency: Annotated[timedelta, BeforeValidator(convert_minutes_to_timedelta)]
    start_date: date
    end_date: date | None = None
    total_doses: int | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_end_condition(self) -> Self:
        if self.end_date is None and self.total_doses is None:
            raise ValueError("Either end_date or total_doses must be provided")
        return self
