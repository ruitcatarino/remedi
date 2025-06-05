from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist

from app.auth import get_user
from app.models.medication import Medication
from app.models.medication_log import MedicationLog
from app.models.user import User
from app.routers.medication import MedicationException
from app.schemas.medication_log import MedicationLogSchema, MedicationLogsSchema

router = APIRouter(prefix="/medication-logs", tags=["medication-logs"])


class MedicationLogException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No medication logs found"
        )


@router.get("/", response_model=list[MedicationLogSchema])
async def get_medication_logs(user: User = Depends(get_user)):
    """Get all medication logs for the current user"""
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
    """Get all medication logs for a specific medication for the current user"""
    try:
        medication = await Medication.get(
            person__user=user, id=medication_id
        ).prefetch_related("person")
    except DoesNotExist:
        raise MedicationException
    logs = await MedicationLog.filter(medication=medication).prefetch_related(
        "schedule", "medication__person"
    )
    if not logs:
        raise MedicationLogException
    return {"medication": medication, "logs": logs}
