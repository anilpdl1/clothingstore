from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = None


class LoginIn(BaseModel):
    # Seed accounts use the reserved .test domain, which EmailStr rejects
    # before the login route can look up the user.
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_login_email(cls, value: str):
        try:
            return validate_email(
                value, check_deliverability=False, test_environment=True
            ).normalized
        except EmailNotValidError as error:
            raise ValueError(str(error)) from error


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class CategoryIn(BaseModel):
    name: str
    slug: str


class VariantIn(BaseModel):
    size: str
    color: str
    sku: str
    stock_quantity: int = Field(ge=0)
    price_override: float | None = None


class ProductIn(BaseModel):
    name: str
    slug: str
    description: str
    price: float = Field(gt=0)
    discount_price: float | None = None
    category_id: int
    brand: str | None = None
    material: str | None = None
    gender: str | None = None
    image_url: str | None = None
    status: bool = True
    variants: list[VariantIn]


class CartItemIn(BaseModel):
    product_variant_id: int
    quantity: int = Field(ge=1)


class QuantityIn(BaseModel):
    quantity: int = Field(ge=1)


class AddressIn(BaseModel):
    line1: str
    line2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    is_default: bool = False


class ProfileIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str | None = None


class PasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


class ReviewIn(BaseModel):
    order_id: int
    rating: int = Field(ge=1, le=5)
    title: str = Field(min_length=2, max_length=140)
    comment: str = Field(min_length=5, max_length=3000)


class HelpfulVoteIn(BaseModel):
    vote: bool


class ReviewReportIn(BaseModel):
    reason: str = Field(
        pattern="^(Spam|Offensive content|Fake review|Irrelevant|Harassment|Other)$"
    )
    description: str | None = Field(default=None, max_length=1000)


class PaymentCreateIn(BaseModel):
    address_id: int


class OrderStatusIn(BaseModel):
    order_status: str
