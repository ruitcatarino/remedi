from datetime import datetime

from pydantic import BaseModel

from app.schemas.medication import MedicationSchema
from app.schemas.medication_schedule import MedicationScheduleSchema


class MedicationLogSchema(BaseModel):
    id: int
    schedule: MedicationScheduleSchema | None
    taken_at: datetime


class MedicationLogsSchema(BaseModel):
    medication: MedicationSchema
    logs: list[MedicationLogSchema]
