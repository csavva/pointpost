from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import app.core.config as config


engine = create_async_engine(config.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


# Database dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session