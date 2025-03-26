import contextlib
import time

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from pyttings import settings
from tortoise import fields
from tortoise.models import Model

ph = PasswordHasher()


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
    async def register(cls, password: str, **kwargs) -> "User":
        return await super().create(
            password=await cls._hash_password(password), **kwargs
        )

    @classmethod
    async def from_jwt(cls, token: str) -> "User":
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return await cls.get(id=payload["id"], email=payload["email"])

    @property
    def access_token(self) -> str:
        return jwt.encode(
            {
                "email": self.email,
                "id": self.id,
                "exp": time.time() + settings.JWT_EXPIRATION,
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    async def _hash_password(password: str) -> str:
        return ph.hash(password)

    async def check_password(self, password: str) -> bool:
        with contextlib.suppress(VerificationError):
            return ph.verify(self.password, password)
        return False
