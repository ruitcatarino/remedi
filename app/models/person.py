from tortoise import fields
from tortoise.models import Model


class Person(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="persons")
    name = fields.CharField(max_length=50)
    birth_date = fields.DateField()
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
