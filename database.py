import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from models import Base


DATABASE_URL = f"sqlite+aiosqlite:///{settings.db_path}"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created via SQLAlchemy!")

if __name__ == "__main__":
    asyncio.run(init_db()) 
