from collections import defaultdict
from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from pyttings import settings
from tortoise.exceptions import DoesNotExist

from app.auth import get_user
from app.models.medication import Medication
from app.models.medication_schedule import MedicationSchedule
from app.models.user import User
from app.routers.medication import MedicationException
from app.schemas.medication_schedule import (
    MedicationScheduleSchema,
    MedicationSchedulesSchema,
)

router = APIRouter(prefix="/medication-schedules", tags=["medication-schedules"])


@router.get("/", response_model=list[MedicationSchedulesSchema])
async def get_medications_schedules(
    medication_id: Annotated[
        int | None, Query(description="Filter by medication ID")
    ] = None,
    medication_name: Annotated[
        str | None, Query(description="Filter by medication name")
    ] = None,
    person_id: Annotated[int | None, Query(description="Filter by person ID")] = None,
    person_name: Annotated[
        str | None, Query(description="Filter by person name")
    ] = None,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Maximum number of results")
    ] = 100,
    user: User = Depends(get_user),
):
    """Retrieve medication schedules with optional filtering."""
    query = Medication.filter(person__user=user)

    if medication_id is not None:
        query = query.filter(id=medication_id)
    elif medication_name is not None:
        query = query.filter(name__icontains=medication_name)

    if person_id is not None:
        query = query.filter(person__id=person_id)
    elif person_name is not None:
        query = query.filter(person__name__icontains=person_name)

    return [
        {"medication": medication, "schedules": list(medication.schedules)}
        for medication in await query.filter(is_active=True)
        .limit(limit)
        .prefetch_related("schedules", "person")
    ]


@router.get("/now", response_model=list[MedicationSchedulesSchema])
async def get_medications_schedules_now(
    medication_id: Annotated[
        int | None, Query(description="Filter by medication ID")
    ] = None,
    medication_name: Annotated[
        str | None, Query(description="Filter by medication name")
    ] = None,
    person_id: Annotated[int | None, Query(description="Filter by person ID")] = None,
    person_name: Annotated[
        str | None, Query(description="Filter by person name")
    ] = None,
    user: User = Depends(get_user),
):
    """Retrieve medication schedules within the grace period with optional filtering."""
    grace_period = timedelta(minutes=settings.MEDICATION_GRACE_PERIOD)
    now = datetime.now(ZoneInfo("UTC"))
    query = MedicationSchedule.filter(
        medication__person__user=user,
        medication__is_prn=False,
        medication__is_active=True,
        scheduled_datetime__gt=now - grace_period,
        scheduled_datetime__lt=now + grace_period,
    )

    if medication_id is not None:
        query = query.filter(medication___id=medication_id)
    elif medication_name is not None:
        query = query.filter(medication___name__icontains=medication_name)

    if person_id is not None:
        query = query.filter(medication___person__id=person_id)
    elif person_name is not None:
        query = query.filter(medication___person__name__icontains=person_name)

    result: dict[Medication, list[MedicationSchedule]] = defaultdict(list)
    for medication_schedule in await query.prefetch_related(
        "medication", "medication__person"
    ):
        result[medication_schedule.medication].append(medication_schedule)

    return [
        {"medication": medication, "schedules": schedules}
        for medication, schedules in result.items()
    ]

@router.get("/{medication_id}", response_model=list[MedicationScheduleSchema])
async def get_medication_schedule_by_id(
    medication_id: int,
    user: User = Depends(get_user),
):
    """Retrieve a specific medication schedule by medication ID."""
    try:
        medication = await Medication.get(
            person__user=user, id=medication_id
        ).prefetch_related("schedules")
        return medication.schedules
    except DoesNotExist:
        raise MedicationException