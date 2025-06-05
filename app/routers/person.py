from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.auth import get_user
from app.logs import logger
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonRegisterSchema, PersonSchema, PersonUpdateSchema

router = APIRouter(prefix="/persons", tags=["persons"])


class PersonException(HTTPException):
    def __init__(
        self,
        detail: str = "Person not found",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PersonSchema)
async def create_person(
    person_model: PersonRegisterSchema, user: User = Depends(get_user)
):
    """Create a new person"""
    try:
        logger.info(f"Creating person: {person_model.name} for user: {user.id}")
        return await Person.create(user=user, **person_model.model_dump())
    except IntegrityError:
        logger.exception(
            f"Person creation failed - duplicate name: {person_model.name} "
            f"for user: {user.id}"
        )
        raise PersonException(
            detail=f"Person with name '{person_model.name}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


@router.get("/", response_model=list[PersonSchema])
async def get_user_persons(
    show_inactive: Annotated[bool, Query(description="Show inactive Persons")] = False,
    user: User = Depends(get_user),
):
    """Get all persons for the current user"""
    query = Person.filter(user=user)

    if not show_inactive:
        query = query.filter(is_active=True)

    return await query.all()


@router.get("/{person_id}", response_model=PersonSchema)
async def get_person(person_id: int, user: User = Depends(get_user)):
    """Get a specific person by ID"""
    try:
        return await Person.get(user=user, id=person_id)
    except DoesNotExist:
        raise PersonException


@router.put("/{person_id}", response_model=PersonSchema)
async def update_person(
    person_id: int, person_model: PersonUpdateSchema, user: User = Depends(get_user)
):
    """Update a person"""
    try:
        person = await Person.get(user=user, id=person_id, is_active=True)

        for attr, value in person_model.model_dump(exclude_unset=True).items():
            setattr(person, attr, value)

        await person.save()
        logger.info(f"Updated person: {person_id} for user: {user.id}")
        return person
    except DoesNotExist:
        raise PersonException
    except IntegrityError:
        raise PersonException(
            detail="Update failed due to constraint violation",
            status_code=status.HTTP_409_CONFLICT,
        )


@router.patch("/disable/{person_id}")
async def disable_person(person_id: int, user: User = Depends(get_user)):
    """Disable a person (soft delete)"""
    try:
        person = await Person.get(user=user, id=person_id, is_active=True)
        person.is_active = False
        await person.save()
        logger.info(f"Disabled person: {person_id} for user: {user.id}")
        return {"message": f"Person '{person.name}' disabled successfully"}
    except DoesNotExist:
        raise PersonException


@router.patch("/enable/{person_id}")
async def enable_person(person_id: int, user: User = Depends(get_user)):
    """Enable a person"""
    try:
        person = await Person.get(user=user, id=person_id, is_active=False)
        person.is_active = True
        await person.save()
        logger.info(f"Enabled person: {person_id} for user: {user.id}")
        return {"message": f"Person '{person.name}' enabled successfully"}
    except DoesNotExist:
        raise PersonException


@router.delete("/{person_id}")
async def delete_person(person_id: int, user: User = Depends(get_user)):
    try:
        person = await Person.get(user=user, id=person_id)
        await person.delete()
        logger.info(f"Deleted person: {person_id} ({person.name}) for user: {user.id}")
        return {"message": f"Person '{person.name}' deleted successfully"}
    except DoesNotExist:
        raise PersonException
