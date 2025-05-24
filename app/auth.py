from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError

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

    try:
        user = await User.from_jwt(token)
        return user
    except (DecodeError, ExpiredSignatureError):
        raise AuthenticationError("Invalid or expired token")
    except Exception:
        raise AuthenticationError("User not found or token invalid")
