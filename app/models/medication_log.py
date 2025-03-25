from tortoise import fields
from tortoise.models import Model


class MedicationLog(Model):
    id = fields.IntField(pk=True)
    medication = fields.ForeignKeyField("models.Medication", related_name="logs")
    schedule = fields.TimeDeltaField()
    taken_at = fields.DatetimeField()
    skipped = fields.BooleanField(default=False)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "medications_logs"
