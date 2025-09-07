from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import AuthIn, AuthOut, SignupIn, UserOut
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Support either model attribute name for the stored password hash
PWD_FIELD = (
    "hashed_password" if hasattr(User, "hashed_password")
    else ("password_hash" if hasattr(User, "password_hash") else None)
)
if not PWD_FIELD:
    raise RuntimeError(
        "User model must have a password hash column named 'hashed_password' or 'password_hash'."
    )


@router.post("/signup")
def signup(data: SignupIn, db: Session = Depends(get_db)) -> dict:
    email = data.email.lower().strip()
    # case-insensitive unique email
    exists = db.query(User).filter(func.lower(User.email) == email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email_exists")

    user = User(name=data.name.strip(), email=email)
    setattr(user, PWD_FIELD, hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True}


@router.post("/login", response_model=AuthOut)
def login(data: AuthIn, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found")

    stored_hash = getattr(user, PWD_FIELD, None)
    if not stored_hash or not verify_password(data.password, stored_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_password")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,            # <-- keep this name for the frontend
        "token_type": "bearer",
        "user": UserOut(id=user.id, name=user.name, email=user.email),
    }
