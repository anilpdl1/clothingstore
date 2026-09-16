from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(value: str):
    return pwd_context.hash(value)


def verify_password(value: str, hashed: str):
    return pwd_context.verify(value, hashed)


def create_token(user_id: int, role: str):
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "role": role, "exp": expires},
        settings.secret_key,
        algorithm=ALGORITHM,
    )
