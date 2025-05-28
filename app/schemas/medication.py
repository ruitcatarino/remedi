from datetime import datetime, timedelta
from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, model_validator

from app.schemas.person import PersonSchema


def convert_minutes_to_timedelta(value: int | None) -> timedelta | None:
    """Converts a frequency in minutes to a timedelta object."""
    if value is None:
        return None
    if isinstance(value, int):
        return timedelta(minutes=value)
    raise ValueError("Frequency must be an integer (minutes)")


def convert_timedelta_to_minutes(value: timedelta | None) -> int | None:
    """Converts a timedelta object to a frequency in minutes."""
    if value is None:
        return None
    return value.total_seconds() // 60


class MedicationSchema(BaseModel):
    id: int
    person: PersonSchema
    name: str
    dosage: str
    is_prn: bool = False
    start_date: datetime
    end_date: datetime | None = None
    frequency: Annotated[int, BeforeValidator(convert_timedelta_to_minutes)] | None = (
        None
    )
    total_doses: int | None = None
    notes: str | None = None


class MedicationRegisterSchema(BaseModel):
    name: str
    person_id: int
    dosage: str
    is_prn: bool = False
    start_date: datetime
    end_date: datetime | None = None
    frequency: (
        Annotated[timedelta, BeforeValidator(convert_minutes_to_timedelta)] | None
    ) = None
    total_doses: int | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_end_condition(self) -> Self:
        if self.end_date is None and self.total_doses is None:
            raise ValueError("Either end_date or total_doses must be provided")
        if self.frequency is None and self.is_prn is False:
            raise ValueError("Frequency must be provided for non-PRN medications")
        return self
