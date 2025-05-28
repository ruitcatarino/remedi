from datetime import datetime, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

from tortoise import fields
from tortoise.models import Model

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
    medication = fields.ForeignKeyField(
        "models.Medication", related_name="schedules", db_index=True
    )
    scheduled_datetime = fields.DatetimeField()
    status = fields.CharEnumField(MedicationStatus, default=MedicationStatus.SCHEDULED)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        indexes = [
            ("medication", "status"),
            ("scheduled_datetime", "status"),
        ]
        unique_together = ("medication", "scheduled_datetime")

    @classmethod
    async def init_medication_schedules(cls, medication: Medication) -> None:
        """
        Create medication schedules for a medication based on start date, frequency,
        and total doses for the first 24 hours.
        """
        if medication.is_prn:
            return

        start_date: datetime = medication.start_date
        end_date: datetime | None = medication.end_date
        frequency: timedelta | None = medication.frequency
        total_doses: int | None = medication.total_doses

        assert frequency is not None, (
            "Frequency must be provided for non-PRN medications"
        )

        now = datetime.now(ZoneInfo("UTC"))
        current_datetime = start_date if start_date > now else now
        schedule_end = start_date + timedelta(days=1)

        if end_date is not None and schedule_end > end_date:
            schedule_end = end_date

        schedules_to_create = []

        while current_datetime < schedule_end:
            if total_doses is not None and len(schedules_to_create) >= total_doses:
                break

            schedules_to_create.append(
                cls(
                    medication=medication,
                    scheduled_datetime=current_datetime,
                    status=MedicationStatus.SCHEDULED,
                )
            )

            current_datetime += frequency

        if schedules_to_create:
            await cls.bulk_create(schedules_to_create)
