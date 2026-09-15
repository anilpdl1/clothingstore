from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models import User, Role
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def current_user(token:str=Depends(oauth2_scheme), db:Session=Depends(get_db)):
    try: user_id=int(jwt.decode(token,settings.secret_key,algorithms=["HS256"]).get("sub"))
    except (JWTError,TypeError,ValueError): raise HTTPException(status_code=401,detail="Invalid or expired token")
    user=db.get(User,user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401,detail="Account unavailable")
    return user
def admin_user(user:User=Depends(current_user)):
    if user.role != Role.ADMIN: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Administrator access required")
    return user
