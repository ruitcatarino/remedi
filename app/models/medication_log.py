from tortoise import fields
from tortoise.models import Model


class MedicationLog(Model):
    id = fields.IntField(primary_key=True)
    medication = fields.ForeignKeyField(
        "models.Medication", related_name="logs", db_index=True
    )
    schedule = fields.ForeignKeyField(
        "models.MedicationSchedule", related_name="log", null=True
    )
    taken_at = fields.DatetimeField(db_index=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        indexes = (("medication", "taken_at"))
