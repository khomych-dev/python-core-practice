from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import AsyncSessionLocal
from models import UserDB
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
)
from limiter import limiter

import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class UserCreate(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register_user(
    request: Request, user: UserCreate, db: AsyncSession = Depends(get_db)
):
    stmt = select(UserDB).where(UserDB.username == user.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(user.password)

    new_user = UserDB(
        username=user.username, hashed_password=hashed_pwd, role="mechanic"
    )

    db.add(new_user)
    await db.commit()

    return {"message": f"Mechanic {user.username} registered successfully!"}


@router.post("/login")
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserDB).where(UserDB.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        token_type: str | None = payload.get("type")

        if token_type != "access":
            raise HTTPException(
                status_code=401, detail="Invalid token type. Expected access token."
            )

        if username is None or role is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

        return {"username": username, "role": role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Token expired. Please log in again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token. Access denied.")


async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Operation not permitted. Admins only."
        )
    return current_user


@router.post("/refresh")
async def refresh_token_endpoint(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    token = request.refresh_token

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if username is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        stmt = select(UserDB).where(UserDB.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists")

        new_access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )

        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Refresh token expired. Please log in again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
