from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from pyttings import settings
from tortoise import fields
from tortoise.models import Model

from app.logs import logger
from app.models.medication_log import MedicationLog

if TYPE_CHECKING:
    from app.models.medication import Medication


class MedicationStatus(StrEnum):
    SCHEDULED = "scheduled"  # Created but not yet due
    NOTIFIED = "notified"  # Reminder sent
    TAKEN = "taken"  # Medication was taken
    LATE_TAKEN = "late_taken"  # Taken after scheduled time but within grace period
    SKIPPED = "skipped"  # User marked as skipped
    MISSED = "missed"  # Past grace period, not taken


class MedicationSchedule(Model):
    id = fields.IntField(primary_key=True)
    medication: fields.ForeignKeyRelation[Medication] = fields.ForeignKeyField(
        "models.Medication", related_name="schedules", db_index=True
    )
    scheduled_datetime = fields.DatetimeField()
    status = fields.CharEnumField(MedicationStatus, default=MedicationStatus.SCHEDULED)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    log: fields.ReverseRelation[MedicationLog]

    class Meta:
        indexes = (
            ("medication", "status"),
            ("scheduled_datetime", "status"),
        )
        unique_together = ("medication", "scheduled_datetime")

    @property
    def in_grace_period(self) -> bool:
        """Returns True if the medication is within the grace period."""
        grace_period = timedelta(minutes=settings.MEDICATION_GRACE_PERIOD)
        now = datetime.now(ZoneInfo("UTC"))
        return now - grace_period <= self.scheduled_datetime <= now + grace_period

    async def handle_take_medication(self) -> None:
        logger.info(f"Taking medication: {self}")
        await MedicationLog.create(
            medication=self.medication,
            schedule=self,
            taken_at=datetime.now(ZoneInfo("UTC")),
        )
        self.status = MedicationStatus.TAKEN
        await self.save()

    async def handle_late_taken(self) -> None:
        logger.info(f"Taking medication late: {self}")
        await MedicationLog.create(
            medication=self.medication,
            schedule=self,
            taken_at=datetime.now(ZoneInfo("UTC")),
        )
        self.status = MedicationStatus.LATE_TAKEN
        await self.save()

    async def handle_medication_notification(self) -> None:
        logger.info(f"Sending notification: {self}")
        # TODO: send notification
        self.status = MedicationStatus.NOTIFIED
        await self.save()

    async def handle_skipped(self) -> None:
        logger.info(f"Skipping medication: {self}")
        self.status = MedicationStatus.SKIPPED
        await self.save()

    async def handle_missed_medication(self) -> None:
        logger.info(f"Missed medication: {self}")
        self.status = MedicationStatus.MISSED
        await self.save()

    def __str__(self) -> str:
        return (
            f"MedicationSchedule(id={self.id}, "
            f"scheduled_datetime={self.scheduled_datetime}, status={self.status})"
        )
