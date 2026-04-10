import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

from models import Base
from auth import get_db
from api import app

load_dotenv()

TEST_DB_URL = os.getenv("DATABASE_URL_TEST")

if TEST_DB_URL is None:
    raise ValueError("CRITICAL ERROR: DATABASE_URL_TEST not found in the .env file!")

engine_test = create_async_engine(TEST_DB_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
