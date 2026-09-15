from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.dependencies.auth import admin_user
from app.models import User,Order,Product,ProductVariant,PaymentStatus,OrderStatus,Review,ReviewStatus,ReviewReport
from sqlalchemy.orm import joinedload
from app.schemas.schemas import OrderStatusIn
router=APIRouter(prefix="/api/admin",tags=["Administration"])
@router.get("/dashboard")
def dashboard(db:Session=Depends(get_db),_=Depends(admin_user)):
    revenue=db.query(func.coalesce(func.sum(Order.total_amount),0)).filter(Order.payment_status==PaymentStatus.PAID).scalar()
    review_average=db.query(func.avg(Review.rating)).filter(Review.status==ReviewStatus.APPROVED).scalar()
    return {"total_revenue":float(revenue),"total_orders":db.query(Order).count(),"total_users":db.query(User).count(),"total_products":db.query(Product).filter_by(status=True).count(),"pending_orders":db.query(Order).filter(Order.order_status==OrderStatus.PENDING).count(),"review_analytics":{"average_store_rating":round(float(review_average),1) if review_average else 0,"total_reviews":db.query(Review).count(),"verified_reviews":db.query(Review).filter_by(verified_purchase=True).count(),"pending_reviews":db.query(Review).filter_by(status=ReviewStatus.PENDING).count(),"reported_reviews":db.query(ReviewReport).filter_by(status="OPEN").count()},"low_stock":[{"id":v.id,"sku":v.sku,"stock_quantity":v.stock_quantity,"product":v.product.name} for v in db.query(ProductVariant).filter(ProductVariant.stock_quantity<10).limit(10)]}
@router.get("/orders")
def all_orders(db:Session=Depends(get_db),_=Depends(admin_user)): return [{"id":o.id,"order_number":o.order_number,"customer":o.user.email,"total":float(o.total_amount),"status":o.order_status,"payment_status":o.payment_status} for o in db.query(Order).order_by(Order.created_at.desc()).all()]
@router.put("/orders/{order_id}/status")
def set_status(order_id:int,data:OrderStatusIn,db:Session=Depends(get_db),_=Depends(admin_user)):
    o=db.get(Order,order_id)
    if not o:raise HTTPException(404,"Order not found")
    try:o.order_status=OrderStatus(data.order_status)
    except ValueError:raise HTTPException(422,"Invalid order status")
    db.commit();return {"id":o.id,"order_status":o.order_status}
@router.get("/users")
def users(db:Session=Depends(get_db),_=Depends(admin_user)):return [{"id":u.id,"name":u.name,"email":u.email,"role":u.role,"active":u.is_active} for u in db.query(User).all()]
def review_row(r):return {"id":r.id,"product":r.product.name,"user":r.user.name,"rating":r.rating,"title":r.title,"comment":r.comment,"status":r.status,"verified_purchase":r.verified_purchase,"created_at":r.created_at,"reports":len(r.reports)}
@router.get("/reviews")
def reviews(status:str|None=None,db:Session=Depends(get_db),_=Depends(admin_user)):
    q=db.query(Review).options(joinedload(Review.product),joinedload(Review.user),joinedload(Review.reports))
    if status:q=q.filter(Review.status==status)
    return [review_row(r) for r in q.order_by(Review.created_at.desc()).all()]
@router.put("/reviews/{review_id}/approve")
def approve_review(review_id:int,db:Session=Depends(get_db),_=Depends(admin_user)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"Review not found")
    r.status=ReviewStatus.APPROVED;db.commit();return {"id":r.id,"status":r.status}
@router.put("/reviews/{review_id}/reject")
def reject_review(review_id:int,db:Session=Depends(get_db),_=Depends(admin_user)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"Review not found")
    r.status=ReviewStatus.REJECTED;db.commit();return {"id":r.id,"status":r.status}
@router.delete("/reviews/{review_id}")
def remove_review(review_id:int,db:Session=Depends(get_db),_=Depends(admin_user)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"Review not found")
    db.delete(r);db.commit();return {"message":"Review deleted"}
@router.get("/review-reports")
def review_reports(db:Session=Depends(get_db),_=Depends(admin_user)):
    return [{"id":x.id,"review_id":x.review_id,"reason":x.reason,"description":x.description,"status":x.status,"reporter":x.user.name} for x in db.query(ReviewReport).options(joinedload(ReviewReport.user)).filter_by(status="OPEN").all()]
