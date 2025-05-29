from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pyttings import settings

from app.auth import get_user, security
from app.logs import logger
from app.models.token_blacklist import BlacklistedToken
from app.models.user import User
from app.schemas.user import UserLoginSchema, UserSchema

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
async def register(user_model: UserSchema) -> dict:
    """Register endpoint."""
    if settings.ALLOW_REGISTRATION is False or await User.exists(
        email=user_model.email
    ):
        logger.error(f"Registration error for user: {user_model.email}")
        raise HTTPException(status_code=400, detail="Registration error")

    await User.register(**user_model.model_dump())
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user_model: UserLoginSchema) -> dict:
    """Login endpoint."""
    user = await User.get_or_none(email=user_model.email, disabled=False)

    if user is None or not await user.check_password(user_model.password):
        logger.error(f"Login error for user: {user_model.email}")
        raise HTTPException(status_code=400, detail="Login error")

    return {
        "message": "User logged in successfully",
        "token": user.access_token,
    }


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Logout endpoint, requires a valid JWT."""
    if await BlacklistedToken.is_token_blacklisted(credentials.credentials):
        logger.error(
            f"Attempted logout with blacklisted token: {credentials.credentials}"
        )
        raise HTTPException(status_code=401, detail="Logout error")

    current_user: User = await get_user(credentials)
    await BlacklistedToken.blacklist_token(credentials.credentials, current_user)

    return {"message": f"User {current_user.email} logged out successfully"}
