from datetime import datetime

from pydantic import BaseModel

from app.schemas.medication import MedicationSchema


class MedicationScheduleSchema(BaseModel):
    id: int
    status: str
    scheduled_datetime: datetime


class MedicationSchedulesSchema(BaseModel):
    medication: MedicationSchema
    schedules: list[MedicationScheduleSchema]
