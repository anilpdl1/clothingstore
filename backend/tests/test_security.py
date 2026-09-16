from app.core.security import hash_password, verify_password, create_token
from jose import jwt
from app.core.config import settings


def test_password_hashing():
    hashed = hash_password("safe-password")
    assert hashed != "safe-password"
    assert verify_password("safe-password", hashed)


def test_token_carries_identity_and_role():
    token = create_token(7, "ADMIN")
    claims = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    assert claims["sub"] == "7" and claims["role"] == "ADMIN"
