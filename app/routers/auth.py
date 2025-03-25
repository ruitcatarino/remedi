from fastapi import APIRouter, HTTPException
from pyttings import settings

from app.models.user import User
from app.schemas.user import UserSchema

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterError(HTTPException):
    """Generic exception for registration errors."""

    def __init__(self):
        super().__init__(status_code=400, detail="Registration error")


@router.post("/register")
async def register(user_model: UserSchema):
    if settings.ALLOW_REGISTRATION is False:
        raise RegisterError

    if await User.exists(email=user_model.email):
        raise RegisterError

    await User.register(**user_model.model_dump())
    return {"message": f"User registered successfully"}
