
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Numeric,
    Boolean,
    Text,
    Enum as SAEnum,
    UniqueConstraint,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ============================================================
# ENUMS
# ============================================================

class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class InteractionType(str, Enum):
    VIEW = "VIEW"
    ADD_TO_CART = "ADD_TO_CART"
    PURCHASE = "PURCHASE"
    RATING = "RATING"
    WISHLIST = "WISHLIST"


# ============================================================
# TIMESTAMP MIXIN
# ============================================================

class Timestamp:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


# ============================================================
# USER
# ============================================================

class User(Base, Timestamp):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    role: Mapped[Role] = mapped_column(
        SAEnum(Role),
        default=Role.USER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    addresses: Mapped[list[Address]] = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    cart: Mapped[Cart | None] = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    orders: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="user",
    )

    reviews: Mapped[list[Review]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    review_votes: Mapped[list[ReviewHelpfulVote]] = relationship(
        "ReviewHelpfulVote",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    review_reports: Mapped[list[ReviewReport]] = relationship(
        "ReviewReport",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    interactions: Mapped[list[UserInteraction]] = relationship(
        "UserInteraction",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ============================================================
# CATEGORY
# ============================================================

class Category(Base, Timestamp):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    products: Mapped[list[Product]] = relationship(
        "Product",
        back_populates="category",
    )


# ============================================================
# PRODUCT
# ============================================================

class Product(Base, Timestamp):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(180),
        index=True,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    brand: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )

    material: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(30),
        index=True,
        nullable=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        index=True,
        nullable=False,
    )

    category: Mapped[Category] = relationship(
        "Category",
        back_populates="products",
    )

    variants: Mapped[list[ProductVariant]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    reviews: Mapped[list[Review]] = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    interactions: Mapped[list[UserInteraction]] = relationship(
        "UserInteraction",
        back_populates="product",
        cascade="all, delete-orphan",
    )


# ============================================================
# PRODUCT VARIANT
# ============================================================

class ProductVariant(Base, Timestamp):
    __tablename__ = "product_variants"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "size",
            "color",
            name="uq_variant_option",
        ),
        Index(
            "ix_variant_stock",
            "stock_quantity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    size: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    color: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True,
        nullable=False,
    )

    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    price_override: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    product: Mapped[Product] = relationship(
        "Product",
        back_populates="variants",
    )


# ============================================================
# CART
# ============================================================

class Cart(Base, Timestamp):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="cart",
    )

    items: Mapped[list[CartItem]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )


# ============================================================
# CART ITEM
# ============================================================

class CartItem(Base, Timestamp):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "product_variant_id",
            name="uq_cart_variant",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cart: Mapped[Cart] = relationship(
        "Cart",
        back_populates="items",
    )

    variant: Mapped[ProductVariant] = relationship(
        "ProductVariant",
    )


# ============================================================
# ADDRESS
# ============================================================

class Address(Base, Timestamp):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    line1: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    line2: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    city: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    postal_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(80),
        default="Nepal",
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="addresses",
    )


# ============================================================
# ORDER
# ============================================================

class Order(Base, Timestamp):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id"),
        nullable=False,
    )

    order_number: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        index=True,
        nullable=False,
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    shipping_cost: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    order_status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="orders",
    )

    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payment: Mapped[Payment | None] = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )


# ============================================================
# ORDER ITEM
# ============================================================

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id"),
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    size: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    color: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    total_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    order: Mapped[Order] = relationship(
        "Order",
        back_populates="items",
    )


# ============================================================
# PAYMENT
# ============================================================

class Payment(Base, Timestamp):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        unique=True,
        nullable=False,
    )

    gateway_transaction_uuid: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    gateway_reference_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(8),
        default="NPR",
        nullable=False,
    )

    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    payment_method: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    order: Mapped[Order] = relationship(
        "Order",
        back_populates="payment",
    )


# ============================================================
# REVIEW
# ============================================================

class Review(Base, Timestamp):
    __tablename__ = "reviews"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            "order_id",
            name="uq_review_per_order_product",
        ),
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_review_rating_range",
        ),
        Index(
            "ix_review_product_status",
            "product_id",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
    )

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    verified_purchase: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    status: Mapped[ReviewStatus] = mapped_column(
        SAEnum(ReviewStatus),
        default=ReviewStatus.APPROVED,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="reviews",
    )

    product: Mapped[Product] = relationship(
        "Product",
        back_populates="reviews",
    )

    order: Mapped[Order] = relationship(
        "Order",
    )

    votes: Mapped[list[ReviewHelpfulVote]] = relationship(
        "ReviewHelpfulVote",
        back_populates="review",
        cascade="all, delete-orphan",
    )

    reports: Mapped[list[ReviewReport]] = relationship(
        "ReviewReport",
        back_populates="review",
        cascade="all, delete-orphan",
    )


# ============================================================
# REVIEW HELPFUL VOTE
# ============================================================

class ReviewHelpfulVote(Base, Timestamp):
    __tablename__ = "review_helpful_votes"

    __table_args__ = (
        UniqueConstraint(
            "review_id",
            "user_id",
            name="uq_helpful_vote",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    vote: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    review: Mapped[Review] = relationship(
        "Review",
        back_populates="votes",
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="review_votes",
    )


# ============================================================
# REVIEW REPORT
# ============================================================

class ReviewReport(Base, Timestamp):
    __tablename__ = "review_reports"

    __table_args__ = (
        UniqueConstraint(
            "review_id",
            "user_id",
            name="uq_review_report",
        ),
        Index(
            "ix_report_status",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="OPEN",
        nullable=False,
    )

    review: Mapped[Review] = relationship(
        "Review",
        back_populates="reports",
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="review_reports",
    )


# ============================================================
# USER PRODUCT INTERACTION
# ============================================================

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    __table_args__ = (
        Index(
            "ix_interaction_user_event",
            "user_id",
            "event_type",
        ),
        Index(
            "ix_interaction_product_event",
            "product_id",
            "event_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_type: Mapped[InteractionType] = mapped_column(
        SAEnum(InteractionType),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="interactions",
    )

    product: Mapped[Product] = relationship(
        "Product",
        back_populates="interactions",
    )
