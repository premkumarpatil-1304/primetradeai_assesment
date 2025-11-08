from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # user id as str
    role: str
