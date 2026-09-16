import base64
import hashlib
import hmac
import json
import uuid
from decimal import Decimal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import (
    CartItem,
    InteractionType,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    ProductVariant,
    User,
    UserInteraction,
)
from app.schemas.schemas import PaymentCreateIn
from app.services.commerce import cart_summary, price, validate_checkout

router = APIRouter(prefix="/api/payments", tags=["Payments"])
TEST_GATEWAY_AMOUNT = Decimal("100000")


def require_esewa_settings() -> None:
    if not settings.esewa_secret_key or not settings.esewa_product_code:
        raise HTTPException(503, "eSewa payments are not configured")


def signature(fields: dict[str, object], names: str) -> str:
    message = ",".join(f"{name}={fields[name]}" for name in names.split(","))
    digest = hmac.new(
        settings.esewa_secret_key.encode(), message.encode(), hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode()


def amount_text(amount: object) -> str:
    value = Decimal(str(amount)).quantize(Decimal("0.01"))
    return format(value, "f").rstrip("0").rstrip(".")


def complete_payment(payment: Payment, reference_id: str, db: Session) -> None:
    if payment.status == PaymentStatus.PAID:
        return

    order = payment.order
    for line in order.items:
        variant = (
            db.query(ProductVariant)
            .filter_by(id=line.product_variant_id)
            .with_for_update()
            .first()
        )
        if not variant or variant.stock_quantity < line.quantity:
            raise HTTPException(
                409, "Stock changed before payment confirmation; contact support"
            )
        variant.stock_quantity -= line.quantity
        db.add(
            UserInteraction(
                user_id=order.user_id,
                product_id=variant.product_id,
                event_type=InteractionType.PURCHASE,
            )
        )

    payment.gateway_reference_id = reference_id
    payment.status = PaymentStatus.PAID
    order.payment_status = PaymentStatus.PAID
    order.order_status = OrderStatus.CONFIRMED
    db.query(CartItem).filter_by(cart_id=order.user.cart.id).delete()


@router.post("/create-order")
def create_payment_order(
    data: PaymentCreateIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    require_esewa_settings()
    cart = validate_checkout(db, user.id, data.address_id)
    summary = cart_summary(db, user.id)
    gateway_amount = TEST_GATEWAY_AMOUNT
    transaction_uuid = f"ORD-{uuid.uuid4().hex[:24]}"
    order = Order(
        user_id=user.id,
        address_id=data.address_id,
        order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
        subtotal=summary["subtotal"],
        discount=summary["discount"],
        shipping_cost=summary["shipping"],
        total_amount=gateway_amount,
    )
    db.add(order)
    db.flush()
    for item in cart.items:
        variant = item.variant
        db.add(
            OrderItem(
                order_id=order.id,
                product_variant_id=variant.id,
                product_name=variant.product.name,
                size=variant.size,
                color=variant.color,
                quantity=item.quantity,
                unit_price=price(variant),
                total_price=price(variant) * item.quantity,
            )
        )

    total = amount_text(gateway_amount)
    fields: dict[str, object] = {
        "amount": total,
        "tax_amount": "0",
        "total_amount": total,
        "transaction_uuid": transaction_uuid,
        "product_code": settings.esewa_product_code,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": f"{settings.backend_public_url.rstrip('/')}/api/payments/esewa/success",
        "failure_url": f"{settings.backend_public_url.rstrip('/')}/api/payments/esewa/failure",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
    }
    fields["signature"] = signature(fields, str(fields["signed_field_names"]))
    db.add(
        Payment(
            order_id=order.id,
            gateway_transaction_uuid=transaction_uuid,
            amount=gateway_amount,
            currency="NPR",
            payment_method="ESEWA",
        )
    )
    db.commit()
    return {"form_url": settings.esewa_form_url, "fields": fields, "currency": "NPR"}



@router.get("/esewa/success", include_in_schema=False)
def esewa_success(data: str = Query(...), db: Session = Depends(get_db)):
    try:
     
        print("Received data:", data)

        payload = json.loads(base64.b64decode(data).decode())

       

        names = payload["signed_field_names"]
        received_signature = payload["signature"]

        generated_signature = signature(payload, names)

        

        if not hmac.compare_digest(
            generated_signature,
            received_signature
        ):
            raise ValueError("Invalid eSewa response signature")

        if payload.get("status") != "COMPLETE":
            raise ValueError(
                f"eSewa payment status is: {payload.get('status')}"
            )

        payment = (
            db.query(Payment)
            .filter_by(
                gateway_transaction_uuid=payload["transaction_uuid"]
            )
            .first()
        )

      
        if not payment:
            raise ValueError("Payment record not found")

        if payload.get("product_code") != settings.esewa_product_code:
            raise ValueError("Product code mismatch")

        if Decimal(str(payload.get("total_amount"))) != Decimal(
            str(payment.amount)
        ):
            raise ValueError(
                f"Amount mismatch: "
                f"eSewa={payload.get('total_amount')} "
                f"database={payment.amount}"
            )

        response = httpx.get(
            settings.esewa_status_url,
            params={
                "product_code": settings.esewa_product_code,
                "total_amount": amount_text(payment.amount),
                "transaction_uuid": payment.gateway_transaction_uuid,
            },
            timeout=15,
        )


        response.raise_for_status()

        status = response.json()

        if status.get("status") != "COMPLETE":
            raise ValueError(
                f"eSewa status verification failed: {status}"
            )

        print("eSewa payment verified successfully!")

        complete_payment(
            payment,
            str(payload.get("transaction_code", "")),
            db,
        )

        db.commit()

        print("Order updated successfully!")

        target = (
            f"{settings.frontend_url.rstrip('/')}"
            f"/profile?payment=success"
        )

    except Exception as e:
        db.rollback()
        target = (
            f"{settings.frontend_url.rstrip('/')}"
            f"/profile?payment=verification-pending"
        )

    return RedirectResponse(target, status_code=303)



@router.get("/esewa/failure", include_in_schema=False)
def esewa_failure() -> RedirectResponse:
    return RedirectResponse(
        f"{settings.frontend_url.rstrip('/')}/checkout?payment=failed", status_code=303
    )
