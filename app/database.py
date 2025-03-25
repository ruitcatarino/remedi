from pyttings import settings
from tortoise import Tortoise


async def init_db() -> None:
    await Tortoise.init(
        db_url=f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()
