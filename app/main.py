from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pyttings import settings

from app.database import close_db, init_db
from app.routers import ROUTERS
from app.scheduler import Scheduler

scheduler = Scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.start()
    yield
    scheduler.shutdown()
    await close_db()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def maintenance_mode(request: Request, call_next):
    if settings.MAINTENANCE_MODE:
        return JSONResponse(status_code=503, content={"detail": "Maintenance mode"})
    return await call_next(request)


for router in ROUTERS:
    app.include_router(router)


@app.get("/")
async def welcome():
    return {"message": "Welcome to Remedi!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
