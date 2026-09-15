from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models import Cart, CartItem, ProductVariant, Address
from app.core.config import settings
def get_cart(db:Session,user_id:int):
    cart=db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.variant).joinedload(ProductVariant.product)).filter(Cart.user_id==user_id).first()
    if not cart: cart=Cart(user_id=user_id); db.add(cart); db.flush()
    return cart
def price(v): return Decimal(str(v.price_override or v.product.discount_price or v.product.price))
def cart_summary(db:Session,user_id:int):
    cart=get_cart(db,user_id); subtotal=sum((price(i.variant)*i.quantity for i in cart.items),Decimal("0")); shipping=Decimal("0") if subtotal>=Decimal("999") else (Decimal(str(settings.shipping_flat_rate)) if subtotal else Decimal("0"))
    return {"id":cart.id,"items":[{"id":i.id,"quantity":i.quantity,"variant_id":i.variant.id,"size":i.variant.size,"color":i.variant.color,"stock":i.variant.stock_quantity,"product":{"id":i.variant.product.id,"name":i.variant.product.name,"image_url":i.variant.product.image_url},"unit_price":float(price(i.variant)),"line_total":float(price(i.variant)*i.quantity)} for i in cart.items],"subtotal":float(subtotal),"discount":0,"shipping":float(shipping),"total":float(subtotal+shipping)}
def validate_checkout(db:Session,user_id:int,address_id:int):
    cart=get_cart(db,user_id)
    if not cart.items: raise HTTPException(400,"Your cart is empty")
    if not db.query(Address).filter_by(id=address_id,user_id=user_id).first(): raise HTTPException(404,"Address not found")
    for item in cart.items:
        variant=db.query(ProductVariant).filter(ProductVariant.id==item.product_variant_id).with_for_update().first()
        if not variant or not variant.is_active or variant.stock_quantity<item.quantity: raise HTTPException(409,"An item is no longer available in the requested quantity")
    return cart
