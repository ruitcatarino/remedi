from tortoise import fields
from tortoise.models import Model


class Medication(Model):
    id = fields.IntField(primary_key=True)
    person = fields.ForeignKeyField(
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

    class Meta:
        indexes = [("start_date", "end_date", "is_active", "is_prn")]
