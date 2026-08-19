import asyncio
import os
from datetime import date

import pytest

# Must happen before `app.*` is imported anywhere: ENABLE_TEST_AUTH gates the
# /auth/test-login route registration at import time, and DATABASE_URL is
# read once when app.database builds its engine. DATABASE_URL is force-set
# (not setdefault) so tests never run against an ambient DATABASE_URL that
# might point at a real dev database -- this suite truncates tables between
# every test.
os.environ["ENABLE_TEST_AUTH"] = "true"
os.environ["ENABLE_DEV_ENDPOINTS"] = "false"
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL_TEST", "postgresql+asyncpg://todo:todo@localhost:5432/todo_test"
)

from app import clock  # noqa: E402
from app.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _database_schema():
    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    yield

    async def _drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(_drop())


@pytest.fixture(autouse=True)
def _clean_tables():
    async def _truncate():
        async with engine.begin() as conn:
            await conn.execute(Base.metadata.tables["tasks"].delete())
            await conn.execute(Base.metadata.tables["lists"].delete())
            await conn.execute(Base.metadata.tables["users"].delete())

    asyncio.run(_truncate())
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _login(client: TestClient, provider_user_id: str = "user-1", provider: str = "google"):
    resp = client.post(
        "/auth/test-login",
        json={
            "provider": provider,
            "provider_user_id": provider_user_id,
            "email": f"{provider_user_id}@example.com",
            "display_name": provider_user_id,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture
def auth_client(client):
    _login(client)
    return client


@pytest.fixture
def second_auth_client():
    with TestClient(app) as c:
        _login(c, provider_user_id="user-2")
        yield c


@pytest.fixture
def frozen_clock():
    fixed = date(2026, 8, 19)
    clock.set_override(fixed)
    yield fixed
    clock.set_override(None)
