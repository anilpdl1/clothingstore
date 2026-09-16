from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root@localhost/clothing_ecommerce"
    secret_key: str = "replace-me-in-production"
    access_token_expire_minutes: int = 30
    esewa_product_code: str = "EPAYTEST"
    esewa_secret_key: str = ""
    esewa_form_url: str = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
    esewa_status_url: str = "https://uat.esewa.com.np/api/epay/transaction/status/"
    # Must be a public URL registered with eSewa; localhost cannot receive the
    # redirect from eSewa's servers in a real end-to-end payment.
    backend_public_url: str = "http://127.0.0.1:8000"
    frontend_url: str = "http://localhost:5173"
    shipping_flat_rate: int = 99
    # Support both a backend-local .env and the repository-level .env used by
    # docker-compose.  Environment variables always take precedence.
    model_config = SettingsConfigDict(
        env_file=(PROJECT_DIR / ".env", BACKEND_DIR / ".env"),
        extra="ignore",
    )


settings = Settings()
