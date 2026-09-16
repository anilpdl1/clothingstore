import pytest
from pydantic import ValidationError

from app.schemas.schemas import LoginIn


def test_login_schema_accepts_the_seed_test_domain():
    data=LoginIn(email="admin@threadline.test",password="AdminPass123!")
    assert data.email=="admin@threadline.test"


def test_login_schema_rejects_an_invalid_email():
    with pytest.raises(ValidationError):
        LoginIn(email="not-an-email",password="password")
