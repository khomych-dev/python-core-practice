import asyncio
import aiosqlite
from config import settings


async def init_db():
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS cars (plate_number TEXT PRIMARY KEY, status TEXT
                         )
                         """)
        await db.commit()
        print("The database and the 'cars' table have been successfully created!")

if __name__ == "__main__":
    asyncio.run(init_db()) 
