from tortoise import fields
from tortoise.models import Model

from app.models.medication import Medication
from app.models.user import User


class Person(Model):
    id = fields.IntField(primary_key=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="persons", db_index=True
    )
    name = fields.CharField(max_length=50)
    birth_date = fields.DateField()
    is_active = fields.BooleanField(default=True, db_index=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    medications: fields.ReverseRelation[Medication]

    class Meta:
        unique_together = ("user", "name")
