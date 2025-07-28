import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.core.database import get_db, Base
from app.models.user import User, UserRole
from app.services.auth_service import auth_service


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = await auth_service.create_user(
        db_session, 
        "test@example.com", 
        UserRole.CONSUMER
    )
    return user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    """Create a test admin user."""
    user = await auth_service.create_user(
        db_session, 
        "admin@example.com", 
        UserRole.ADMIN
    )
    return user


@pytest.fixture
async def test_enterprise_user(db_session: AsyncSession) -> User:
    """Create a test enterprise user."""
    user = await auth_service.create_user(
        db_session, 
        "enterprise@example.com", 
        UserRole.ENTERPRISE
    )
    return user


@pytest.fixture
async def access_token(test_user: User) -> str:
    """Create an access token for test user."""
    token = await auth_service.create_access_token({"sub": str(test_user.id)})
    return token


@pytest.fixture
async def admin_access_token(test_admin_user: User) -> str:
    """Create an access token for admin user."""
    token = await auth_service.create_access_token({"sub": str(test_admin_user.id)})
    return token


@pytest.fixture
async def enterprise_access_token(test_enterprise_user: User) -> str:
    """Create an access token for enterprise user."""
    token = await auth_service.create_access_token({"sub": str(test_enterprise_user.id)})
    return token