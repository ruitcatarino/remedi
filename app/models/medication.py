from tortoise import fields
from tortoise.models import Model


class Medication(Model):
    id = fields.IntField(pk=True)
    person = fields.ForeignKeyField("models.Person", related_name="medications")
    name = fields.CharField(max_length=50)
    dosage = fields.CharField(max_length=50)
    frequency = fields.TimeDeltaField()
    start_date = fields.DateField()
    end_date = fields.DateField(null=True)
    total_doses = fields.IntField(null=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "medications"
