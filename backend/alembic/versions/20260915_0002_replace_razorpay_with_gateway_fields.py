"""rename Razorpay-specific payment columns to gateway-neutral fields

Revision ID: 20260915_0002
Revises: 20260915_0001
Create Date: 2026-09-15 00:10:00
"""

import sqlalchemy as sa
from alembic import op


revision = "20260915_0002"
down_revision = "20260915_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("payments", "razorpay_order_id", new_column_name="gateway_transaction_uuid", existing_type=sa.String(100), existing_nullable=False)
    op.alter_column("payments", "razorpay_payment_id", new_column_name="gateway_reference_id", existing_type=sa.String(100), existing_nullable=True)


def downgrade() -> None:
    op.alter_column("payments", "gateway_reference_id", new_column_name="razorpay_payment_id", existing_type=sa.String(100), existing_nullable=True)
    op.alter_column("payments", "gateway_transaction_uuid", new_column_name="razorpay_order_id", existing_type=sa.String(100), existing_nullable=False)
