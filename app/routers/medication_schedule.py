from typing import Any

from fastapi import APIRouter, Depends

from app.auth import get_user
from app.models.medication import Medication
from app.models.user import User
from app.routers.medication import MedicationException
from app.schemas.medication_schedule import (
    MedicationSchedulesSchema,
)

router = APIRouter(prefix="/schedule", tags=["Medication Schedule"])


@router.get("/filters", response_model=list[MedicationSchedulesSchema])
async def get_medications_schedules(
    medication_id: int | None = None,
    medication_name: str | None = None,
    person_id: int | None = None,
    person_name: str | None = None,
    user: User = Depends(get_user),
):
    filter: dict[str, Any] = {"person__user": user}

    if medication_id is not None:
        filter["id"] = medication_id
    elif medication_name is not None:
        filter["name"] = medication_name

    if person_id is not None:
        filter["person__id"] = person_id
    elif person_name is not None:
        filter["person__name"] = person_name

    medications = await Medication.filter(**filter, is_active=True).prefetch_related(
        "schedules", "person"
    )
    if not medications:
        raise MedicationException

    return [
        {"medication": medication, "schedules": list(medication.schedules)}
        for medication in medications
    ]
