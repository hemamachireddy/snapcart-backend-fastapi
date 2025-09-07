from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import os

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET", "change_me_now")
ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(payload: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    if expires_minutes is None:
        expires_minutes = DEFAULT_EXPIRE_MINUTES
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """Return JWT payload or raise 401 if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # 401 to match auth expectations
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
