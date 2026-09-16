from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token
from app.dependencies.auth import current_user
from app.models import User, Cart
from app.schemas.schemas import RegisterIn, LoginIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email.lower()).first():
        raise HTTPException(409, "Email is already registered")
    user = User(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        phone=data.phone,
    )
    db.add(user)
    db.flush()
    db.add(Cart(user_id=user.id))
    db.commit()
    return TokenOut(
        access_token=create_token(user.id, user.role.value), role=user.role.value
    )

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return TokenOut(
        access_token=create_token(user.id, user.role.value), role=user.role.value
    )


@router.get("/me")
def me(user: User = Depends(current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
    }
