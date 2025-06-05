from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from tortoise.exceptions import DoesNotExist, IntegrityError
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

router = APIRouter(prefix="/medications", tags=["medications"])


class MedicationException(HTTPException):
    def __init__(
        self,
        detail: str = "Medication not found",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MedicationSchema)
async def create_medication(
    medication_model: MedicationRegisterSchema, user: User = Depends(get_user)
):
    """Create a new medication and schedule it"""
    try:
        person = await Person.get(
            user=user, id=medication_model.person_id, is_active=True
        )
    except DoesNotExist:
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

    return medication


@router.post("/intake/{medication_id}")
async def handle_medication_intake(
    medication_id: int,
    is_missed_dose: Annotated[bool, Query(description="Is missed dose")] = False,
    user: User = Depends(get_user),
):
    """Handle medication intake"""
    try:
        medication = await Medication.get(
            person__user=user, id=medication_id, is_active=True
        )
    except DoesNotExist:
        raise MedicationException
    await medication.handle_medication_intake(is_missed_dose)
    return {"message": "Medication intake handled successfully"}


@router.post("/bulk-intake")
async def handle_bulk_medication_intake(
    payload: BulkInktakeMedicationSchema, user: User = Depends(get_user)
):
    """Handle bulk medication intake"""
    medications = await Medication.filter(
        person__user=user, id__in=payload.medication_ids
    )
    for medication in medications:
        await medication.handle_medication_intake(
            medication.id in payload.missed_doses_ids
        )
    return {"message": "Bulk medication intake handled successfully"}


@router.get("/", response_model=list[MedicationSchema])
async def get_medications(
    show_inactive: Annotated[
        bool, Query(description="Show inactive medications")
    ] = False,
    user: User = Depends(get_user),
):
    query = Medication.filter(person__user=user)
    if not show_inactive:
        query = query.filter(is_active=True, person__is_active=True)
    return await query.prefetch_related("person")


@router.get("/filter", response_model=MedicationSchema)
async def get_medication_with_filters(
    medication_name: Annotated[str, Query(description="Filter by medication name")],
    person_name: Annotated[str, Query(description="Filter by person name")],
    show_inactive: Annotated[
        bool, Query(description="Show inactive medications")
    ] = False,
    user: User = Depends(get_user),
):
    """Get a medication by name and person name"""
    query = Medication.filter(
        person__user=user,
        person__name__icontains=person_name,
        name__icontains=medication_name,
    )
    if not show_inactive:
        query = query.filter(is_active=True, person__is_active=True)
    medication = await query.prefetch_related("person")
    if medication is None:
        raise MedicationException
    return medication


@router.get("/{medication_id}", response_model=MedicationSchema)
async def get_medication_by_id(medication_id: int, user: User = Depends(get_user)):
    """Get a specific medication by ID"""
    try:
        return await Medication.get(
            person__user=user, id=medication_id
        ).prefetch_related("person")
    except DoesNotExist:
        raise MedicationException


@router.get("/person/{person_id}", response_model=list[MedicationSchema])
async def get_medications_by_person_id(
    person_id: int,
    show_inactive: Annotated[
        bool, Query(description="Show inactive medications")
    ] = False,
    user: User = Depends(get_user),
):
    """Get all medications by person ID"""
    query = Medication.filter(person__user=user, person__id=person_id)
    if not show_inactive:
        query = query.filter(is_active=True)
    return await query.all().prefetch_related("person")


@router.patch("/disable/{medication_id}")
async def disable_medication(medication_id: int, user: User = Depends(get_user)):
    """Disable a medication"""
    try:
        medication = await Medication.get(
            person__user=user, id=medication_id, is_active=True
        )
    except DoesNotExist:
        raise MedicationException
    medication.is_active = False
    await medication.save()
    await medication.delete_future_schedules()
    return {"message": "Medication disabled successfully"}


@router.patch("/enable/{medication_id}")
async def enable_medication(medication_id: int, user: User = Depends(get_user)):
    """Enable a medication"""
    try:
        medication = await Medication.get(
            person__user=user, id=medication_id, is_active=False
        )
    except DoesNotExist:
        raise MedicationException
    medication.is_active = True
    await medication.save()
    await medication.generate_schedules()
    return {"message": "Medication enabled successfully"}
