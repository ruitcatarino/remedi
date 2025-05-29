from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_user
from app.logs import logger
from app.models.medication import Medication
from app.models.person import Person
from app.models.user import User
from app.routers.person import PersonException
from app.schemas.medication import (
    MedicationRegisterSchema,
    MedicationSchema,
)
from app.utils.date import to_utc

router = APIRouter(
    prefix="/medication",
    tags=["Medication"],
)


class MedicationException(HTTPException):
    def __init__(self, detail: str = "Medication not found"):
        super().__init__(status_code=400, detail=detail)


@router.post("/register")
async def register(
    medication_model: MedicationRegisterSchema, user: User = Depends(get_user)
):
    person = await Person.get_or_none(user=user, id=medication_model.person_id)
    if person is None:
        raise PersonException

    medication_model.start_date = to_utc(medication_model.start_date, user.timezone)
    if medication_model.end_date is not None:
        medication_model.end_date = to_utc(medication_model.end_date, user.timezone)
        if medication_model.end_date < medication_model.start_date:
            raise HTTPException(
                status_code=400, detail="End date must be after start date"
            )

    if medication_model.start_date < datetime.now(ZoneInfo("UTC")) - timedelta(
        minutes=1
    ):
        raise HTTPException(status_code=400, detail="Start date must be in the future")

    logger.info(f"Registering medication: {medication_model}")
    medication = await Medication.create(person=person, **medication_model.model_dump())
    await medication.generate_schedules()
    return {"message": "Medication registered successfully"}


@router.get("/", response_model=list[MedicationSchema])
async def get_medications(user: User = Depends(get_user)):
    medications = await Medication.filter(person__user=user).prefetch_related("person")
    if not medications:
        raise MedicationException
    return medications


@router.get("/{id}", response_model=MedicationSchema)
async def get_medication(id: int, user: User = Depends(get_user)):
    medication = await Medication.get_or_none(person__user=user, id=id)
    if medication is None:
        raise MedicationException
    return medication


@router.get("/name/{name}", response_model=MedicationSchema)
async def get_medication_by_name(name: str, user: User = Depends(get_user)):
    medication = await Medication.get_or_none(person__user=user, name=name)
    if medication is None:
        raise MedicationException
    return medication


@router.delete("/")
async def delete_medications(user: User = Depends(get_user)):
    if not await Medication.exists(person__user=user):
        raise MedicationException
    await Medication.filter(person__user=user).delete()
    return {"message": "Medications deleted successfully"}


@router.delete("/{id}")
async def delete_medication(id: int, user: User = Depends(get_user)):
    if not await Medication.exists(person__user=user, id=id):
        raise MedicationException
    await Medication.filter(person__user=user, id=id).delete()
    return {"message": "Medication deleted successfully"}
