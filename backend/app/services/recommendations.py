"""Replaceable rule-based hybrid recommender; keep this API stable for future ML rankers."""
from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func
from app.models import Product,ProductVariant,OrderItem,Order,PaymentStatus,UserInteraction,InteractionType,Review,ReviewStatus
def card(p,score=None):
    ratings=[r.rating for r in p.reviews if r.status==ReviewStatus.APPROVED]
    output={"id":p.id,"name":p.name,"slug":p.slug,"price":float(p.discount_price or p.price),"image_url":p.image_url,"brand":p.brand,"rating":round(sum(ratings)/len(ratings),1) if ratings else None,"review_count":len(ratings)}
    if score is not None: output["score"]=round(score,2)
    return output
def available(db): return db.query(Product).options(joinedload(Product.variants),joinedload(Product.reviews)).filter(Product.status==True,Product.variants.any(ProductVariant.stock_quantity>0))
def similar(db, product_id, limit=8):
    source=db.get(Product,product_id)
    if not source:return []
    candidates=available(db).filter(Product.id!=source.id).all(); ranked=[]
    for p in candidates:
        score=(4 if p.category_id==source.category_id else 0)+(2 if p.gender and p.gender==source.gender else 0)+(1.5 if p.brand and p.brand==source.brand else 0)
        price_gap=abs(float(p.price)-float(source.price))/max(float(source.price),1);score+=max(0,1-price_gap)
        if score:ranked.append((score,p))
    return [card(p,s) for s,p in sorted(ranked,key=lambda x:x[0],reverse=True)[:limit]]
def frequently_bought(db, product_id, limit=6):
    target_orders=db.query(OrderItem.order_id).join(ProductVariant).filter(ProductVariant.product_id==product_id).subquery()
    rows=(available(db).join(ProductVariant).join(OrderItem).join(Order).filter(OrderItem.order_id.in_(target_orders),Product.id!=product_id,Order.payment_status==PaymentStatus.PAID).group_by(Product.id).order_by(func.count(OrderItem.id).desc()).limit(limit).all())
    return [card(p) for p in rows]
def popular(db, limit=8):
    rows=(available(db).outerjoin(UserInteraction).group_by(Product.id).order_by(func.count(UserInteraction.id).desc(),Product.created_at.desc()).limit(limit).all())
    return [card(p) for p in rows]
def personalized(db,user_id,limit=8):
    preferred=[x[0] for x in db.query(Product.category_id).join(UserInteraction).filter(UserInteraction.user_id==user_id).group_by(Product.category_id).order_by(func.count(UserInteraction.id).desc()).limit(3)]
    purchased=[x[0] for x in db.query(ProductVariant.product_id).join(OrderItem).join(Order).filter(Order.user_id==user_id,Order.payment_status==PaymentStatus.PAID).all()]
    query=available(db).filter(~Product.id.in_(purchased))
    if preferred: query=query.order_by(Product.category_id.in_(preferred).desc(),Product.created_at.desc())
    rows=query.limit(limit).all()
    return [card(p) for p in rows] if rows else popular(db,limit)
