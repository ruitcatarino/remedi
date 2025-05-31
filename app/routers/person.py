from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_user
from app.logs import logger
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonRegisterSchema, PersonSchema, PersonUpdateSchema

router = APIRouter(
    prefix="/person",
    tags=["Person"],
)


class PersonException(HTTPException):
    def __init__(self, detail: str = "Person not found"):
        super().__init__(status_code=400, detail=detail)


@router.post("/register")
async def register(person_model: PersonRegisterSchema, user: User = Depends(get_user)):
    """Register a person endpoint."""

    if await Person.exists(user=user, name=person_model.name):
        logger.error(f"Person registration error for person: {person_model.name}")
        raise PersonException(detail="Person registration error")

    logger.info(f"Registering person: {person_model}")
    await Person.create(user=user, **person_model.model_dump())

    return {"message": "Person registered successfully"}


@router.get("/", response_model=list[PersonSchema])
async def get_persons(show_inactive: bool = False, user: User = Depends(get_user)):
    filters = {"user": user}
    if not show_inactive:
        filters["is_active"] = True
    persons = await Person.filter(**filters).all()
    if not persons:
        raise PersonException
    return persons


@router.get("/{id}", response_model=PersonSchema)
async def get_person(id: int, user: User = Depends(get_user)):
    person = await Person.get_or_none(user=user, id=id, is_active=True)
    if person is None:
        raise PersonException
    return person


@router.get("/name/{name}", response_model=PersonSchema)
async def get_person_by_name(name: str, user: User = Depends(get_user)):
    person = await Person.get_or_none(user=user, name=name, is_active=True)
    if person is None:
        raise PersonException
    return person


@router.put("/{id}", response_model=PersonSchema)
async def update_person(
    id: int, person_model: PersonUpdateSchema, user: User = Depends(get_user)
):
    person = await Person.get_or_none(user=user, id=id, is_active=True)

    if person is None:
        raise PersonException

    for attr, value in person_model.model_dump(exclude_unset=True).items():
        setattr(person, attr, value)

    await person.save()
    return person


@router.put("/name/{name}", response_model=PersonSchema)
async def update_person_by_name(
    name: str, person_model: PersonUpdateSchema, user: User = Depends(get_user)
):
    person = await Person.get_or_none(user=user, name=name, is_active=True)

    if person is None:
        raise PersonException

    for attr, value in person_model.model_dump(exclude_unset=True).items():
        setattr(person, attr, value)

    await person.save()
    return person


@router.patch("/disable/{person_id}")
async def disable_person(person_id: int, user: User = Depends(get_user)):
    person = await Person.get_or_none(user=user, id=person_id, is_active=True)
    if person is None:
        raise PersonException

    person.is_active = False
    await person.save()
    return {"message": "Person disabled successfully"}


@router.patch("/enable/{person_id}")
async def enable_person(person_id: int, user: User = Depends(get_user)):
    person = await Person.get_or_none(user=user, id=person_id, is_active=False)
    if person is None:
        raise PersonException

    person.is_active = True
    await person.save()
    return {"message": "Person enabled successfully"}


@router.delete("/")
async def delete_persons(user: User = Depends(get_user)):
    if not await Person.exists(user=user):
        raise PersonException
    logger.info(f"Deleting persons: {user}")
    await Person.filter(user=user).delete()
    return {"message": "Persons deleted successfully"}


@router.delete("/{id}")
async def delete_person(id: int, user: User = Depends(get_user)):
    if not await Person.exists(user=user, id=id):
        raise PersonException
    logger.info(f"Deleting person: {id}")
    await Person.filter(user=user, id=id).delete()
    return {"message": "Person deleted successfully"}


@router.delete("/name/{name}")
async def delete_person_by_name(name: str, user: User = Depends(get_user)):
    if not await Person.exists(user=user, name=name):
        raise PersonException
    logger.info(f"Deleting person: {name}")
    await Person.filter(user=user, name=name).delete()
    return {"message": "Person deleted successfully"}
