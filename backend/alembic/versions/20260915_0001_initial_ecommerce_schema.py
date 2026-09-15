"""create the initial ecommerce schema

Revision ID: 20260915_0001
Revises:
Create Date: 2026-09-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260915_0001"
down_revision = None
branch_labels = None
depends_on = None


role = sa.Enum("USER", "ADMIN", name="role")
payment_status = sa.Enum("PENDING", "PAID", "FAILED", "REFUNDED", name="paymentstatus")
order_status = sa.Enum("PENDING", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED", name="orderstatus")
review_status = sa.Enum("PENDING", "APPROVED", "REJECTED", name="reviewstatus")
interaction_type = sa.Enum("VIEW", "ADD_TO_CART", "PURCHASE", "RATING", "WISHLIST", name="interactiontype")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30)),
        sa.Column("role", role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False), sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False), sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_price", sa.Numeric(12, 2)), sa.Column("brand", sa.String(100)),
        sa.Column("material", sa.String(100)), sa.Column("gender", sa.String(30)), sa.Column("image_url", sa.String(500)),
        sa.Column("status", sa.Boolean(), nullable=False), sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_gender", "products", ["gender"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("size", sa.String(20), nullable=False), sa.Column("color", sa.String(40), nullable=False),
        sa.Column("sku", sa.String(80), nullable=False), sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("price_override", sa.Numeric(12, 2)), sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("product_id", "size", "color", name="uq_variant_option"),
    )
    op.create_index("ix_product_variants_sku", "product_variants", ["sku"], unique=True)
    op.create_index("ix_variant_stock", "product_variants", ["stock_quantity"])
    op.create_table(
        "carts", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "addresses", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("line1", sa.String(200), nullable=False), sa.Column("line2", sa.String(200)),
        sa.Column("city", sa.String(80), nullable=False), sa.Column("state", sa.String(80), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=False), sa.Column("country", sa.String(80), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "orders", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("address_id", sa.Integer(), sa.ForeignKey("addresses.id"), nullable=False),
        sa.Column("order_number", sa.String(40), nullable=False), sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False), sa.Column("shipping_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False), sa.Column("payment_status", payment_status, nullable=False),
        sa.Column("order_status", order_status, nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=True)
    op.create_table(
        "cart_items", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_variant_id", sa.Integer(), sa.ForeignKey("product_variants.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("cart_id", "product_variant_id", name="uq_cart_variant"),
    )
    op.create_table(
        "order_items", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_variant_id", sa.Integer(), sa.ForeignKey("product_variants.id"), nullable=False),
        sa.Column("product_name", sa.String(180), nullable=False), sa.Column("size", sa.String(20), nullable=False),
        sa.Column("color", sa.String(40), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False), sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
    )
    op.create_table(
        "payments", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False, unique=True),
        sa.Column("razorpay_order_id", sa.String(100), nullable=False, unique=True), sa.Column("razorpay_payment_id", sa.String(100), unique=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False), sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("status", payment_status, nullable=False), sa.Column("payment_method", sa.String(40)),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "reviews", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False), sa.Column("title", sa.String(140), nullable=False), sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("verified_purchase", sa.Boolean(), nullable=False), sa.Column("status", review_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "product_id", "order_id", name="uq_review_per_order_product"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )
    op.create_index("ix_review_product_status", "reviews", ["product_id", "status"])
    op.create_table(
        "review_helpful_votes", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("review_id", sa.Integer(), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("vote", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("review_id", "user_id", name="uq_helpful_vote"),
    )
    op.create_table(
        "review_reports", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("review_id", sa.Integer(), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(40), nullable=False), sa.Column("description", sa.Text()), sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("review_id", "user_id", name="uq_review_report"),
    )
    op.create_index("ix_report_status", "review_reports", ["status"])
    op.create_table(
        "user_interactions", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", interaction_type, nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_interaction_user_event", "user_interactions", ["user_id", "event_type"])
    op.create_index("ix_interaction_product_event", "user_interactions", ["product_id", "event_type"])


def downgrade() -> None:
    op.drop_index("ix_interaction_product_event", table_name="user_interactions")
    op.drop_index("ix_interaction_user_event", table_name="user_interactions")
    op.drop_table("user_interactions")
    op.drop_index("ix_report_status", table_name="review_reports")
    op.drop_table("review_reports")
    op.drop_table("review_helpful_votes")
    op.drop_index("ix_review_product_status", table_name="reviews")
    op.drop_table("reviews")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("cart_items")
    op.drop_table("orders")
    op.drop_table("addresses")
    op.drop_table("carts")
    op.drop_index("ix_variant_stock", table_name="product_variants")
    op.drop_index("ix_product_variants_sku", table_name="product_variants")
    op.drop_table("product_variants")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_gender", table_name="products")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
