from fastapi import APIRouter, HTTPException, status
from schemas.auth_schemas import UserCreate, UserLogin, TokenResponse
from models.auth_model import User
from utils import hash_password, verify_password, create_access_token
from config.db import db
from datetime import timedelta

router = APIRouter()

@router.post("/signup")
async def signup(user: UserCreate):
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    user_data = {
        "full_name": user.full_name,
        "email": user.email,
        "hashed_password": hashed
    }

    await db["users"].insert_one(user_data)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    db_user = await db["users"].find_one({"email": user.email})
    
    if not db_user:
        raise HTTPException(status_code=404, detail="This email is not registered")
    
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "full_name": db_user["full_name"],
            "email": db_user["email"]
        }
    }
