from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.models.medication import Medication
    from app.models.medication_schedule import MedicationSchedule


class MedicationLog(Model):
    id = fields.IntField(primary_key=True)
    medication: fields.ForeignKeyRelation[Medication] = fields.ForeignKeyField(
        "models.Medication", related_name="logs", db_index=True
    )
    schedule: fields.ForeignKeyRelation[MedicationSchedule] | None = (
        fields.ForeignKeyField(
            "models.MedicationSchedule", related_name="log", null=True
        )
    )
    taken_at = fields.DatetimeField(db_index=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        indexes = ("medication", "taken_at")
