from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import close_db, init_db
from app.routers import ROUTERS


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)


for router in ROUTERS:
    app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Welcome to Remedi!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
