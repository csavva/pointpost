import pytest_asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
from urllib.parse import urlparse

from app.main import app
from app.db.postgres import Base, get_db
from app.core.config import TEST_DATABASE_URL

parsed_url = urlparse(TEST_DATABASE_URL)

POSTGRES_USER = parsed_url.username
POSTGRES_PASSWORD = parsed_url.password
POSTGRES_HOST = parsed_url.hostname
POSTGRES_PORT = parsed_url.port
ADMIN_DB_NAME = "postgres"
TEST_DB_NAME = parsed_url.path.lstrip("/")

# Save the TEST_DATABASE_URL globally (no engine yet)
_test_database_url = TEST_DATABASE_URL

@pytest_asyncio.fixture(scope="session")
async def setup_test_database():
    # Connect to admin DB and create the test DB
    admin_conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=ADMIN_DB_NAME,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    try:
        await admin_conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        await admin_conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    finally:
        await admin_conn.close()

    # Connect to the new test DB and create tables
    engine = create_async_engine(_test_database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    yield

    # Cleanup: Drop the test DB
    admin_conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=ADMIN_DB_NAME,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    try:
        await admin_conn.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid()
        """)
        await admin_conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    finally:
        await admin_conn.close()

# Correct override: create engine + session at test runtime
async def override_get_db() -> AsyncSession:
    engine = create_async_engine(_test_database_url, echo=True)
    TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def async_client(setup_test_database):
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

async def truncate_tables(session: AsyncSession):
    await session.execute(text('TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE'))
    await session.commit()

@pytest_asyncio.fixture(autouse=True)
async def clean_database(async_client):
    """Clean database before each test."""
    # Get a real database session
    override_db = await override_get_db().__anext__()
    await truncate_tables(override_db)