from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_user
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonFullSchema, PersonSchema

router = APIRouter(
    prefix="/person",
    tags=["Person"],
)


@router.post("/register")
async def register(person_model: PersonSchema, user: User = Depends(get_user)) -> dict:
    """Register a person endpoint."""

    if await Person.exists(user=user, name=person_model.name):
        raise HTTPException(status_code=400, detail="Person registration error")

    await Person.create(user=user, **person_model.model_dump())

    return {"message": "Person registered successfully"}


@router.get("/", response_model=list[PersonFullSchema])
async def get_persons(user: User = Depends(get_user)):
    return await Person.filter(user=user).all()


@router.get("/{id}", response_model=PersonSchema)
async def get_person(id: int, user: User = Depends(get_user)):
    return await Person.get_or_none(user=user, id=id)


@router.get("/name/{name}", response_model=PersonSchema)
async def get_person_by_name(name: str, user: User = Depends(get_user)):
    return await Person.get_or_none(user=user, name=name)


@router.put("/{id}", response_model=PersonSchema)
async def update_person(
    id: int, person_model: PersonSchema, user: User = Depends(get_user)
):
    return await Person.filter(user=user, id=id).update(**person_model.model_dump())


@router.put("/name/{name}", response_model=PersonSchema)
async def update_person_by_name(
    name: str, person_model: PersonSchema, user: User = Depends(get_user)
):
    return await Person.filter(user=user, name=name).update(**person_model.model_dump())


@router.delete("/", response_model=list[PersonFullSchema])
async def delete_persons(user: User = Depends(get_user)):
    return await Person.filter(user=user).delete()


@router.delete("/{id}", response_model=PersonSchema)
async def delete_person(id: int, user: User = Depends(get_user)):
    return await Person.filter(user=user, id=id).delete()


@router.delete("/name/{name}", response_model=PersonSchema)
async def delete_person_by_name(name: str, user: User = Depends(get_user)):
    return await Person.filter(user=user, name=name).delete()
