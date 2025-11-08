# app/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
