import hashlib
import time
from datetime import datetime

import jwt
from pyttings import settings
from tortoise import fields
from tortoise.models import Model

from app.logs import logger
from app.models.user import User


class BlacklistedToken(Model):
    id = fields.IntField(primary_key=True)
    token_hash = fields.CharField(max_length=64, unique=True, db_index=True)
    user = fields.ForeignKeyField("models.User", related_name="blacklisted_tokens")
    expires_at = fields.DatetimeField(db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    reason = fields.CharField(max_length=50, default="logout")

    class Meta:
        table = "blacklisted_tokens"
        indexes = [
            ("token_hash", "expires_at"),
            ("user", "created_at"),
        ]

    @classmethod
    async def blacklist_token(
        cls, token: str, user: User, reason: str = "logout"
    ) -> "BlacklistedToken":
        """Add a token to the blacklist. Token must be a valid JWT token."""
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        expires_at = datetime.fromtimestamp(payload.get("exp", time.time()))

        blacklisted_token, _ = await cls.get_or_create(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            defaults={"user": user, "expires_at": expires_at, "reason": reason},
        )

        return blacklisted_token

    @classmethod
    async def is_token_blacklisted(cls, token: str) -> bool:
        """Check if a token is blacklisted."""
        return await cls.filter(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at__gt=datetime.now(),
        ).exists()

    @classmethod
    async def cleanup_expired_tokens(cls) -> int:
        """
        Remove expired tokens from blacklist to keep table size manageable.
        """
        logger.info("Cleaning up expired tokens from blacklist")
        await cls.filter(expires_at__lt=datetime.now()).delete()

    def __str__(self) -> str:
        return f"BlacklistedToken(user={self.user}, expires_at={self.expires_at})"
