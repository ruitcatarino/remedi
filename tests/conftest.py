import os

import pytest_asyncio
from tortoise import Tortoise


@pytest_asyncio.fixture(scope="function", autouse=True)
async def initialize_tests():
    """Initialize the database for each test. Clean up after each test."""
    await Tortoise.init(
        db_url="sqlite://:memory:", modules={"models": ["app.models", "aerich.models"]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise._drop_databases()


def pytest_configure():
    os.environ["PYTTING_SETTINGS_MODULE"] = "tests.settings"
