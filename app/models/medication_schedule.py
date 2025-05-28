from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


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
    scheduled_datetime = fields.DatetimeField(db_index=True)
    status = fields.CharEnumField(MedicationStatus, default=MedicationStatus.SCHEDULED)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        indexes = [
            ("medication", "status"),
            ("scheduled_datetime", "status"),
        ]
        unique_together = ("medication", "scheduled_datetime")
