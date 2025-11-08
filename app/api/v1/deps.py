# app/api/v1/deps.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings

# -------------------------------------------------------------------
# OAuth2 scheme – tells FastAPI where to find the login endpoint
# -------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# -------------------------------------------------------------------
# Create JWT Access Token
# -------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT token for a given user payload.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


# -------------------------------------------------------------------
# Verify JWT Access Token
# -------------------------------------------------------------------
def verify_access_token(token: str = Depends(oauth2_scheme)):
    """
    Verify JWT access token, decode and return payload (email, role).
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject (email).",
            )

        return {"sub": email, "role": role}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
