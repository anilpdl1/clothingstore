from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import User, CartItem, ProductVariant, UserInteraction, InteractionType
from app.schemas.schemas import CartItemIn, QuantityIn
from app.services.commerce import get_cart, cart_summary

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("")
def read_cart(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return cart_summary(db, user.id)


@router.post("/items", status_code=201)
def add_item(
    data: CartItemIn, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    v = db.get(ProductVariant, data.product_variant_id)
    if not v or not v.is_active or not v.product.status:
        raise HTTPException(404, "Variant unavailable")
    cart = get_cart(db, user.id)
    item = (
        db.query(CartItem).filter_by(cart_id=cart.id, product_variant_id=v.id).first()
    )
    quantity = data.quantity + (item.quantity if item else 0)
    if quantity > v.stock_quantity:
        raise HTTPException(409, "Insufficient stock")
    if item:
        item.quantity = quantity
    else:
        db.add(
            CartItem(cart_id=cart.id, product_variant_id=v.id, quantity=data.quantity)
        )
    db.add(
        UserInteraction(
            user_id=user.id,
            product_id=v.product_id,
            event_type=InteractionType.ADD_TO_CART,
        )
    )
    db.commit()
    return cart_summary(db, user.id)


@router.put("/items/{item_id}")
def update_item(
    item_id: int,
    data: QuantityIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(CartItem)
        .join(CartItem.cart)
        .filter(CartItem.id == item_id, CartItem.cart.has(user_id=user.id))
        .first()
    )
    if not item:
        raise HTTPException(404, "Cart item not found")
    if data.quantity > item.variant.stock_quantity:
        raise HTTPException(409, "Insufficient stock")
    item.quantity = data.quantity
    db.commit()
    return cart_summary(db, user.id)


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart.has(user_id=user.id))
        .first()
    )
    if not item:
        raise HTTPException(404, "Cart item not found")
    db.delete(item)
    db.commit()
    return cart_summary(db, user.id)


@router.delete("")
def clear(user: User = Depends(current_user), db: Session = Depends(get_db)):
    cart = get_cart(db, user.id)
    db.query(CartItem).filter_by(cart_id=cart.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
