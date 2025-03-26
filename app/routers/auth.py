from fastapi import APIRouter, HTTPException
from pyttings import settings

from app.models.user import User
from app.schemas.user import UserLoginSchema, UserSchema

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterError(HTTPException):
    """Generic exception for registration errors."""

    def __init__(self):
        super().__init__(status_code=400, detail="Registration error")


class LoginError(HTTPException):
    """Generic exception for login errors."""

    def __init__(self):
        super().__init__(status_code=401, detail="Login error")


@router.post("/register")
async def register(user_model: UserSchema):
    if settings.ALLOW_REGISTRATION is False or await User.exists(
        email=user_model.email
    ):
        raise RegisterError

    await User.register(**user_model.model_dump())
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user_model: UserLoginSchema):
    user = await User.get_or_none(email=user_model.email)

    if user is None or not await user.check_password(user_model.password):
        raise LoginError

    return {
        "message": "User logged in successfully",
        "token": user.access_token,
    }
