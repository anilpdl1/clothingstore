from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import User, UserInteraction, InteractionType
from app.services.recommendations import (
    similar,
    frequently_bought,
    popular,
    personalized,
)

router = APIRouter(prefix="/api", tags=["Recommendations"])


@router.get("/products/{product_id}/similar")
def get_similar(product_id: int, db: Session = Depends(get_db)):
    return {"items": similar(db, product_id)}


@router.get("/products/{product_id}/frequently-bought-together")
def get_frequently_bought(product_id: int, db: Session = Depends(get_db)):
    return {"items": frequently_bought(db, product_id)}


@router.get("/products/{product_id}/recommended")
def recommended_for_product(product_id: int, db: Session = Depends(get_db)):
    return {"items": similar(db, product_id)}


@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db)):
    return {"strategy": "popular", "items": popular(db)}


@router.get("/recommendations/personalized")
def personal(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"strategy": "personalized", "items": personalized(db, user.id)}


@router.post("/products/{product_id}/interactions", status_code=204)
def track(
    product_id: int,
    event_type: InteractionType,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    # Explicit, small event stream; no anonymous cross-site tracking.
    db.add(
        UserInteraction(user_id=user.id, product_id=product_id, event_type=event_type)
    )
    db.commit()
