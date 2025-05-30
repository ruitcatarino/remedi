from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from app.auth import get_user
from app.logs import logger
from app.models.medication import Medication
from app.models.person import Person
from app.models.user import User
from app.routers.person import PersonException
from app.schemas.medication import (
    BulkInktakeMedicationSchema,
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

    try:
        async with in_transaction():
            medication = await Medication.create(
                person=person, **medication_model.model_dump(exclude_unset=True)
            )
            await medication.generate_schedules()
    except IntegrityError as e:
        logger.exception(f"Medication registration error: {e}")
        raise MedicationException(detail="Medication registration error")

    return {"message": "Medication registered successfully"}


@router.post("/intake/{medication_id}")
async def handle_medication_intake(
    medication_id: int, is_missed_dose: bool = False, user: User = Depends(get_user)
):
    medication = await Medication.get_or_none(person__user=user, id=medication_id)
    if medication is None:
        raise MedicationException
    await medication.handle_medication_intake(is_missed_dose)
    return {"message": "Medication intake handled successfully"}


@router.post("/intake")
async def handle_medication_intake_with_filters(
    medication_name: str,
    person_name: str,
    is_missed_dose: bool = False,
    user: User = Depends(get_user),
):
    person = await Person.get_or_none(user=user, name=person_name)
    if person is None:
        raise PersonException
    medication = await Medication.get_or_none(person=person, name=medication_name)
    if medication is None:
        raise MedicationException
    await medication.handle_medication_intake(is_missed_dose)
    return {"message": "Medication intake handled successfully"}


@router.post("/bulk-intake")
async def handle_bulk_medication_intake(
    payload: BulkInktakeMedicationSchema, user: User = Depends(get_user)
):
    medications = await Medication.filter(
        person__user=user, id__in=payload.medication_ids
    )
    for medication in medications:
        await medication.handle_medication_intake(
            medication.id in payload.missed_doses_ids
        )
    return {"message": "Bulk medication intake handled successfully"}


@router.get("/", response_model=list[MedicationSchema])
async def get_medications(show_inactive: bool = False, user: User = Depends(get_user)):
    filters = {"person__user": user}
    if not show_inactive:
        filters["is_active"] = True
    medications = await Medication.filter(**filters).prefetch_related("person")
    if not medications:
        raise MedicationException
    return medications


@router.get("/filter", response_model=MedicationSchema)
async def get_medication_with_filters(
    medication_name: str, person_name: str, user: User = Depends(get_user)
):
    person = await Person.get_or_none(user=user, name=person_name, is_active=True)
    if person is None:
        raise PersonException
    medication = await Medication.get_or_none(
        person=person, name=medication_name, is_active=True
    ).prefetch_related("person")
    if medication is None:
        raise MedicationException
    return medication


@router.get("/{id}", response_model=MedicationSchema)
async def get_medication(id: int, user: User = Depends(get_user)):
    medication = await Medication.get_or_none(
        person__user=user, id=id
    ).prefetch_related("person")
    if medication is None:
        raise MedicationException
    return medication


@router.put("/disable/{medication_id}")
async def disable_medication(medication_id: int, user: User = Depends(get_user)):
    medication = await Medication.get_or_none(
        person__user=user, id=medication_id, is_active=True
    )
    if medication is None:
        raise MedicationException

    medication.is_active = False
    await medication.save()
    return {"message": "Medication disabled successfully"}


@router.put("/enable/{medication_id}")
async def enable_medication(medication_id: int, user: User = Depends(get_user)):
    medication = await Medication.get_or_none(
        person__user=user, id=medication_id, is_active=False
    )
    if medication is None:
        raise MedicationException

    medication.is_active = True
    await medication.save()
    return {"message": "Medication enabled successfully"}
