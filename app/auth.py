from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.token_blacklist import BlacklistedToken
from app.models.user import User

security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Generic exception for authentication errors."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)


async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    """
    token = credentials.credentials

    if BlacklistedToken.is_token_blacklisted(token):
        raise AuthenticationError

    try:
        return await User.from_jwt(token)
    except Exception:
        raise AuthenticationError
