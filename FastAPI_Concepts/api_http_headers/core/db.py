from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def db_session() -> AsyncIterator[AsyncSession]:
    """
    Database Session Generator.

    :return: A database session.
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def init_db():
    # Import models so they are registered on Base.metadata before create_all.
    import models.api_keys  # noqa: F401
    import models.tenants  # noqa: F401

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise


class Base(DeclarativeBase):
    """
    Base class for defining database tables.
    """

    pass
