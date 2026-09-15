from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session,joinedload
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import User,Order,Address
from app.schemas.schemas import AddressIn,ProfileIn,PasswordIn
from app.core.security import verify_password,hash_password
router=APIRouter(prefix="/api",tags=["Orders and profile"])
def out(o): return {"id":o.id,"order_number":o.order_number,"total_amount":float(o.total_amount),"payment_status":o.payment_status,"order_status":o.order_status,"created_at":o.created_at,"items":[{"product_name":i.product_name,"size":i.size,"color":i.color,"quantity":i.quantity,"unit_price":float(i.unit_price)} for i in o.items]}
@router.get("/orders")
def orders(user:User=Depends(current_user),db:Session=Depends(get_db)):return [out(x) for x in db.query(Order).options(joinedload(Order.items)).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()]
@router.get("/orders/{order_id}")
def order(order_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    o=db.query(Order).options(joinedload(Order.items)).filter_by(id=order_id,user_id=user.id).first()
    if not o:raise HTTPException(404,"Order not found")
    return out(o)
@router.get("/addresses")
def addresses(user:User=Depends(current_user),db:Session=Depends(get_db)): return [{"id":a.id,"line1":a.line1,"line2":a.line2,"city":a.city,"state":a.state,"postal_code":a.postal_code,"country":a.country,"is_default":a.is_default} for a in user.addresses]
@router.put("/profile")
def update_profile(data:ProfileIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    user.name,user.phone=data.name,data.phone;db.commit();return {"id":user.id,"name":user.name,"phone":user.phone}
@router.put("/profile/password")
def change_password(data:PasswordIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not verify_password(data.current_password,user.password_hash):raise HTTPException(400,"Current password is incorrect")
    user.password_hash=hash_password(data.new_password);db.commit();return {"message":"Password changed"}
@router.post("/addresses",status_code=201)
def create_address(data:AddressIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if data.is_default: db.query(Address).filter_by(user_id=user.id).update({"is_default":False})
    a=Address(user_id=user.id,**data.model_dump());db.add(a);db.commit();return {"id":a.id}
@router.put("/addresses/{address_id}")
def update_address(address_id:int,data:AddressIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    a=db.query(Address).filter_by(id=address_id,user_id=user.id).first()
    if not a:raise HTTPException(404,"Address not found")
    if data.is_default:db.query(Address).filter_by(user_id=user.id).update({"is_default":False})
    for key,value in data.model_dump().items():setattr(a,key,value)
    db.commit();return {"id":a.id}
@router.delete("/addresses/{address_id}")
def delete_address(address_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    a=db.query(Address).filter_by(id=address_id,user_id=user.id).first()
    if not a:raise HTTPException(404,"Address not found")
    db.delete(a);db.commit();return {"message":"Address removed"}
