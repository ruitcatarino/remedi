from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_user
from app.models.medication import Medication
from app.models.medication_schedule import MedicationSchedule
from app.models.person import Person
from app.models.user import User
from app.routers.person import PersonException
from app.schemas.medication import MedicationRegisterSchema, MedicationSchema
from app.utils.date import to_utc

router = APIRouter(
    prefix="/medication",
    tags=["Medication"],
)


@router.post("/register")
async def register(
    medication_model: MedicationRegisterSchema, user: User = Depends(get_user)
):
    person = await Person.get_or_none(user=user, id=medication_model.person_id)
    if person is None:
        raise PersonException
    medication_model.start_date = to_utc(medication_model.start_date, user.timezone)
    if medication_model.end_date:
        medication_model.end_date = to_utc(medication_model.end_date, user.timezone)

    if medication_model.start_date < datetime.now(ZoneInfo("UTC")) - timedelta(
        minutes=1
    ):
        raise HTTPException(status_code=400, detail="Start date must be in the future")

    medication = await Medication.create(person=person, **medication_model.model_dump())
    await MedicationSchedule.init_medication_schedules(medication)
    return {"message": "Medication registered successfully"}


@router.get("/", response_model=list[MedicationSchema])
async def get_medications(user: User = Depends(get_user)):
    medications = await Medication.filter(person__user=user).prefetch_related("person")
    if not medications:
        raise HTTPException(status_code=400, detail="Medications not found")
    return medications
