from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.schemas import UserLogin, Token, UserCreate, UserResponse
from app.core.security import create_access_token
from app.core.users import authenticate_user, create_user, get_user
from app.core.config import settings
from app.core.security import get_admin_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de login"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "email": user["email"]
    }


@router.post("/users", response_model=UserResponse, dependencies=[Depends(get_admin_user)])
async def create_new_user(user_data: UserCreate):
    """Crear nuevo usuario (solo admin)"""
    try:
        user = create_user(user_data.email, user_data.password, user_data.role)
        return UserResponse(email=user["email"], role=user["role"], active=user["active"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
