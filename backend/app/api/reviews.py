from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import User,Product,ProductVariant,Order,OrderItem,PaymentStatus,Review,ReviewStatus,ReviewHelpfulVote,ReviewReport,UserInteraction,InteractionType
from app.schemas.schemas import ReviewIn,HelpfulVoteIn,ReviewReportIn
router=APIRouter(prefix="/api",tags=["Reviews"])
def summary(db,product_id):
    rows=db.query(Review.rating,func.count(Review.id)).filter(Review.product_id==product_id,Review.status==ReviewStatus.APPROVED).group_by(Review.rating).all(); counts={rating:count for rating,count in rows};total=sum(counts.values());return {"average_rating":round(sum(r*c for r,c in counts.items())/total,1) if total else 0,"total_reviews":total,"distribution":{str(i):counts.get(i,0) for i in range(1,6)}}
def review_out(r,user_id=None):
    helpful=sum(1 for v in r.votes if v.vote);unhelpful=sum(1 for v in r.votes if not v.vote);mine=next((v.vote for v in r.votes if v.user_id==user_id),None)
    return {"id":r.id,"rating":r.rating,"title":r.title,"comment":r.comment,"status":r.status,"verified_purchase":r.verified_purchase,"created_at":r.created_at,"user_name":r.user.name,"helpful_count":helpful,"unhelpful_count":unhelpful,"my_vote":mine,"is_owner":r.user_id==user_id}
@router.get("/products/{product_id}/reviews")
def list_reviews(product_id:int,rating:int|None=Query(None,ge=1,le=5),verified:bool=False,sort:str="recent",page:int=Query(1,ge=1),limit:int=Query(10,ge=1,le=50),db:Session=Depends(get_db)):
    q=db.query(Review).options(joinedload(Review.user),joinedload(Review.votes)).filter(Review.product_id==product_id,Review.status==ReviewStatus.APPROVED)
    if rating:q=q.filter(Review.rating==rating)
    if verified:q=q.filter(Review.verified_purchase==True)
    if sort=="highest":q=q.order_by(Review.rating.desc(),Review.created_at.desc())
    elif sort=="lowest":q=q.order_by(Review.rating.asc(),Review.created_at.desc())
    elif sort=="helpful":q=q.outerjoin(ReviewHelpfulVote).group_by(Review.id).order_by(func.coalesce(func.sum(ReviewHelpfulVote.vote),0).desc())
    else:q=q.order_by(Review.created_at.desc())
    total=q.count();rows=q.offset((page-1)*limit).limit(limit).all();return {"summary":summary(db,product_id),"items":[review_out(r) for r in rows],"total":total,"page":page,"pages":(total+limit-1)//limit}
@router.post("/products/{product_id}/reviews",status_code=201)
def create_review(product_id:int,data:ReviewIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    product=db.get(Product,product_id);order=db.query(Order).filter_by(id=data.order_id,user_id=user.id,payment_status=PaymentStatus.PAID).first()
    purchased=order and db.query(OrderItem).join(ProductVariant).filter(OrderItem.order_id==order.id,ProductVariant.product_id==product_id).first()
    if not product or not purchased:raise HTTPException(403,"Only customers with a paid purchase can review this product")
    if db.query(Review).filter_by(user_id=user.id,product_id=product_id,order_id=order.id).first():raise HTTPException(409,"You already reviewed this product for this order")
    review=Review(user_id=user.id,product_id=product_id,order_id=order.id,verified_purchase=True,status=ReviewStatus.APPROVED,**data.model_dump(exclude={"order_id"}));db.add(review);db.add(UserInteraction(user_id=user.id,product_id=product_id,event_type=InteractionType.RATING));db.commit();return {"id":review.id}
@router.put("/reviews/{review_id}")
def update_review(review_id:int,data:ReviewIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"Review not found")
    if r.user_id!=user.id:raise HTTPException(403,"You can only edit your own review")
    r.rating,r.title,r.comment=data.rating,data.title,data.comment;db.commit();return {"id":r.id}
@router.delete("/reviews/{review_id}")
def delete_review(review_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"Review not found")
    if r.user_id!=user.id:raise HTTPException(403,"You can only delete your own review")
    db.delete(r);db.commit();return {"message":"Review deleted"}
@router.post("/reviews/{review_id}/helpful")
def helpful(review_id:int,data:HelpfulVoteIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Review,review_id):raise HTTPException(404,"Review not found")
    if db.query(ReviewHelpfulVote).filter_by(review_id=review_id,user_id=user.id).first():raise HTTPException(409,"You already voted on this review")
    db.add(ReviewHelpfulVote(review_id=review_id,user_id=user.id,vote=data.vote));db.commit();return {"message":"Vote recorded"}
@router.delete("/reviews/{review_id}/helpful")
def undo_helpful(review_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    vote=db.query(ReviewHelpfulVote).filter_by(review_id=review_id,user_id=user.id).first()
    if not vote:raise HTTPException(404,"Vote not found")
    db.delete(vote);db.commit();return {"message":"Vote removed"}
@router.post("/reviews/{review_id}/report",status_code=201)
def report_review(review_id:int,data:ReviewReportIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Review,review_id):raise HTTPException(404,"Review not found")
    if db.query(ReviewReport).filter_by(review_id=review_id,user_id=user.id).first():raise HTTPException(409,"You already reported this review")
    db.add(ReviewReport(review_id=review_id,user_id=user.id,**data.model_dump()));db.commit();return {"message":"Report received"}
