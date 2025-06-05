from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned

from app.logs import logger
from app.models.token_blacklist import BlacklistedToken
from app.models.user import User

security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Generic exception for authentication errors."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    """
    token = credentials.credentials

    if await BlacklistedToken.is_token_blacklisted(token):
        logger.warning(f"Attempted login with blacklisted token: {token}")
        raise AuthenticationError

    try:
        return await User.from_jwt(token)
    except (InvalidTokenError, DoesNotExist, MultipleObjectsReturned):
        logger.exception(f"Attempted login with invalid token: {token}")
        raise AuthenticationError
