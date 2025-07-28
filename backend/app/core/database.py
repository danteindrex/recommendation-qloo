from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings
import redis.asyncio as redis


class Base(DeclarativeBase):
    pass


# Database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_db():
    """Database dependency for FastAPI."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis():
    """Redis dependency for FastAPI."""
    return redis_client


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models import user, cultural_data, analytics, admin
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)