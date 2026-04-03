from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import AsyncSessionLocal
from models import UserDB
from security import get_password_hash


router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserCreate(BaseModel):
    username: str
    password: str
    
    
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
@router.post("/register", status_code=201)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(UserDB).where(UserDB.username == user.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user.password)
    
    new_user = UserDB(
        username=user.username, 
        hashed_password=hashed_pwd, 
        role="mechanic"
    )
    
    db.add(new_user)
    await db.commit()
    
    return {"message": f"Mechanic {user.username} registered successfully!"}