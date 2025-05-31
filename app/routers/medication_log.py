from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_user
from app.models.medication import Medication
from app.models.medication_log import MedicationLog
from app.models.user import User
from app.routers.medication import MedicationException
from app.schemas.medication_log import MedicationLogSchema, MedicationLogsSchema

router = APIRouter(prefix="/log", tags=["Medication Log"])


class MedicationLogException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No medication logs found")


@router.get("/", response_model=list[MedicationLogSchema])
async def get_medication_logs(user: User = Depends(get_user)):
    logs = await MedicationLog.filter(medication__person__user=user).prefetch_related(
        "schedule"
    )
    if not logs:
        raise MedicationLogException
    return logs


@router.get("/medication/{medication_id}", response_model=MedicationLogsSchema)
async def get_medication_logs_by_medication_id(
    medication_id: int, user: User = Depends(get_user)
):
    medication = await Medication.get_or_none(
        person__user=user, id=medication_id
    ).prefetch_related("person")
    if medication is None:
        raise MedicationException
    logs = await MedicationLog.filter(medication=medication).prefetch_related(
        "schedule"
    )
    if not logs:
        raise MedicationLogException
    return {"medication": medication, "logs": logs}
