import hashlib

from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=130)
    name = fields.CharField(max_length=50)
    phone_number = fields.CharField(max_length=50)
    birth_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def register(cls, password: str, **kwargs):
        return await super().create(
            password=await cls._hash_password(password), **kwargs
        )

    async def check_password(self, password: str):
        return await self._hash_password(password) == self.password

    @staticmethod
    async def _hash_password(password: str):
        return hashlib.sha512(password.encode("utf-8")).hexdigest()
