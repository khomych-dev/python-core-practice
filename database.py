import asyncio
import aiosqlite

DB_NAME = "garage.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS cars (plate_namber TEXT PRIMARY KEY, status TEXT
                         )
                         """)
        await db.commit()
        print("The database and the 'cars' table have been successfully created!")

if __name__ == "__main__":
    asyncio.run(init_db())
