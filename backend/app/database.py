from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()

# In test mode (ENABLE_TEST_AUTH=true) each test may run its own asyncio event
# loop (fresh TestClient / asyncio.run per test), and pooled asyncpg
# connections can't be reused across loops. NullPool opens a fresh connection
# per checkout instead of caching one, avoiding cross-loop reuse entirely.
# Pooling is only worth it in a long-lived server process, so this doesn't
# affect the real run.
_pool_kwargs = {"poolclass": NullPool} if settings.enable_test_auth else {"pool_pre_ping": True}

engine = create_async_engine(settings.database_url, **_pool_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
