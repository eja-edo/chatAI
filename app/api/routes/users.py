from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user
from app.api.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_api(user_in: UserCreate, db: Session = Depends(get_db)):
    return await create_user(db, user_in)
 

from app.schemas.user import LoginRequest, TokenResponse
from app.models.user import User
from app.core.security import verify_password, create_access_token, create_refresh_token
from sqlalchemy.future import select



@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    token = create_access_token(data={"sub": str(user.id)})
    refresh = create_refresh_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token, refresh_token=refresh)