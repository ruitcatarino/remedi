from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from tortoise import fields
from tortoise.models import Model

from app.logs import logger
from app.models.medication_log import MedicationLog
from app.models.medication_schedule import MedicationSchedule, MedicationStatus

if TYPE_CHECKING:
    from app.models.person import Person


class Medication(Model):
    id = fields.IntField(primary_key=True)
    person: fields.ForeignKeyRelation[Person] = fields.ForeignKeyField(
        "models.Person", related_name="medications", db_index=True
    )
    name = fields.CharField(max_length=50)
    dosage = fields.CharField(max_length=50)
    is_prn = fields.BooleanField(
        default=False, db_index=True
    )  # not scheduled, as needed
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField(null=True)
    frequency = fields.TimeDeltaField(null=True)
    total_doses = fields.IntField(null=True)
    doses_taken = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True, db_index=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    schedules: fields.ReverseRelation[MedicationSchedule]
    logs: fields.ReverseRelation[MedicationLog]

    class Meta:
        unique_together = ("person", "name", "dosage", "start_date")
        indexes = ("start_date", "end_date", "is_active", "is_prn")

    @property
    async def next_scheduled(self) -> MedicationSchedule | None:
        """Returns the next scheduled medication."""
        if self.is_prn or self.is_active is False:
            return None

        return await self.schedules.filter(
            status__in=[MedicationStatus.SCHEDULED, MedicationStatus.NOTIFIED]
        ).earliest("scheduled_datetime")

    @property
    async def next_in_grace(self) -> MedicationSchedule | None:
        """
        Returns the next scheduled medication that is within the grace period.
        """
        next_scheduled: MedicationSchedule | None = await self.next_scheduled

        if next_scheduled is not None and next_scheduled.in_grace_period:
            return next_scheduled

        return None

    @property
    async def last_missed(self) -> MedicationSchedule | None:
        """Returns the last missed medication."""
        if self.is_prn or self.is_active is False:
            return None

        return await self.schedules.filter(status=MedicationStatus.MISSED).latest(
            "scheduled_datetime"
        )

    async def generate_schedules(
        self: Medication, delta: timedelta | None = None
    ) -> None:
        """
        Create medication schedules for a medication for a defined period.
        Skip if already created.
        """
        logger.info(f"Generating medication schedules for: {self}")
        if self.is_prn:
            return

        if delta is None:
            delta = timedelta(days=1)

        now = datetime.now(ZoneInfo("UTC"))
        schedule_end = now + delta
        next_scheduled: MedicationSchedule | None = await self.next_scheduled
        current_datetime = max(
            now if next_scheduled is None else next_scheduled.scheduled_datetime,
            self.start_date,
        )

        if self.end_date is not None and schedule_end > self.end_date:
            schedule_end = self.end_date

        if self.start_date > schedule_end or current_datetime > schedule_end:
            return

        schedules_to_create: list[MedicationSchedule] = []

        while current_datetime <= schedule_end:
            if (
                self.total_doses is not None
                and len(schedules_to_create) >= self.total_doses - self.doses_taken
            ):
                break

            schedules_to_create.append(
                MedicationSchedule(
                    medication=self,
                    scheduled_datetime=current_datetime,
                    status=MedicationStatus.SCHEDULED,
                )
            )

            current_datetime += self.frequency

        if schedules_to_create:
            await MedicationSchedule.bulk_create(
                schedules_to_create, ignore_conflicts=True
            )

    async def handle_medication_intake(self) -> None:
        """Handles medication intake."""
        logger.info(f"Handling medication intake: {self}")

        next_in_grace: MedicationSchedule | None = await self.next_in_grace

        if next_in_grace is None:
            logger.info(f"Taking unscheduled medication: {self}")
            await MedicationLog.create(
                medication=self,
                taken_at=datetime.now(ZoneInfo("UTC")),
            )
        else:
            logger.info(f"Taking scheduled medication: {self} - {next_in_grace}")
            await next_in_grace.handle_take_medication()

        self.doses_taken += 1
        await self.save()
        return

    def __str__(self) -> str:
        return (
            f"Medication(start_date={self.start_date}, end_date={self.end_date}, "
            f"frequency={self.frequency}, total_doses={self.total_doses}, "
            f"doses_taken={self.doses_taken}, is_active={self.is_active})"
        )
