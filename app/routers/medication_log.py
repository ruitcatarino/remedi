from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_user
from app.models.medication_log import MedicationLog
from app.models.user import User
from app.schemas.medication_log import MedicationLogSchema

router = APIRouter(
    prefix="/log",
    tags=["Medication Log"],
)


@router.get("/", response_model=list[MedicationLogSchema])
async def get_medication_logs(user: User = Depends(get_user)):
    logs = await MedicationLog.filter(medication__person__user=user).prefetch_related(
        "schedule"
    )
    if not logs:
        raise HTTPException(status_code=400, detail="No medication logs found")
    return logs
