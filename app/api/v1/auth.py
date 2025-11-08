# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from app.db.mongodb import mongodb
from app.api.v1.deps import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# ✅ SCHEMA
# ============================================================
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"  # Optional, default = user


# ============================================================
# ✅ REGISTER USER
# ============================================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    print("🔥 Register route hit")

    # Check MongoDB connection
    if mongodb.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    users_col = mongodb.db["users"]

    existing = await users_col.find_one({"email": user_in.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password (bcrypt max 72 bytes)
    hashed_pw = pwd_context.hash(user_in.password[:72])

    new_user = {
        "email": user_in.email,
        "password": hashed_pw,
        "role": user_in.role,
    }

    result = await users_col.insert_one(new_user)
    print("✅ User inserted with ID:", result.inserted_id)

    return {"message": "User registered successfully"}


# ============================================================
# ✅ LOGIN USER
# ============================================================
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print("🔑 Login route hit")

    users_col = mongodb.db["users"]

    # Find user by email
    user = await users_col.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    raw_password = form_data.password[:72]

    if not pwd_context.verify(raw_password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Create JWT access token
    access_token_expires = timedelta(hours=1)
    token_data = {"sub": user["email"], "role": user["role"]}
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)

    print(f"✅ Token generated for {user['email']} (role: {user['role']})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user["email"],
        "role": user["role"],
    }
