from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.core.database import get_db
from app.dependencies.auth import admin_user
from app.models import Product, Category, ProductVariant, Review, ReviewStatus
from sqlalchemy import func
from app.schemas.schemas import ProductIn, CategoryIn

router = APIRouter(prefix="/api", tags=["Catalog"])


def product_out(p, rating=None):
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "price": float(p.price),
        "discount_price": float(p.discount_price) if p.discount_price else None,
        "brand": p.brand,
        "gender": p.gender,
        "image_url": p.image_url,
        "category": {"id": p.category.id, "name": p.category.name},
        "rating": rating,
        "variants": [
            {
                "id": v.id,
                "size": v.size,
                "color": v.color,
                "sku": v.sku,
                "stock_quantity": v.stock_quantity,
                "price_override": float(v.price_override) if v.price_override else None,
            }
            for v in p.variants
        ],
    }


@router.get("/products")
def products(
    q: str | None = None,
    category_id: int | None = None,
    gender: str | None = None,
    color: str | None = None,
    size: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool = False,
    sort: str = "newest",
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.variants))
        .filter(Product.status == True)
    )
    if q:
        query = query.filter(
            or_(Product.name.ilike(f"%{q}%"), Product.brand.ilike(f"%{q}%"))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if gender:
        query = query.filter(Product.gender == gender)
    if brand:
        query = query.filter(Product.brand == brand)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if color:
        query = query.join(ProductVariant).filter(ProductVariant.color == color)
    if size:
        query = query.join(ProductVariant).filter(ProductVariant.size == size)
    if in_stock:
        query = query.join(ProductVariant).filter(ProductVariant.stock_quantity > 0)
    ordering = {
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "newest": Product.created_at.desc(),
    }.get(sort, Product.created_at.desc())
    total = query.distinct().count()
    rows = query.order_by(ordering).offset((page - 1) * limit).limit(limit).all()
    return {
        "items": [product_out(x) for x in rows],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/products/{product_id}")
def product(product_id: int, db: Session = Depends(get_db)):
    p = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.variants))
        .filter(Product.id == product_id, Product.status == True)
        .first()
    )
    if not p:
        raise HTTPException(404, "Product not found")
    average, count = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.product_id == p.id, Review.status == ReviewStatus.APPROVED)
        .one()
    )
    return product_out(
        p,
        {
            "average_rating": round(float(average), 1) if average else 0,
            "total_reviews": count,
        },
    )


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return [
        {"id": c.id, "name": c.name, "slug": c.slug}
        for c in db.query(Category).filter_by(is_active=True).all()
    ]


@router.post("/admin/categories", status_code=201)
def create_category(
    data: CategoryIn, db: Session = Depends(get_db), _=Depends(admin_user)
):
    c = Category(**data.model_dump())
    db.add(c)
    db.commit()
    return {"id": c.id, "name": c.name}


@router.put("/admin/categories/{category_id}")
def update_category(
    category_id: int,
    data: CategoryIn,
    db: Session = Depends(get_db),
    _=Depends(admin_user),
):
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(404, "Category not found")
    c.name, c.slug = data.name, data.slug
    db.commit()
    return {"id": c.id, "name": c.name}


@router.delete("/admin/categories/{category_id}")
def deactivate_category(
    category_id: int, db: Session = Depends(get_db), _=Depends(admin_user)
):
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(404, "Category not found")
    c.is_active = False
    db.commit()
    return {"message": "Category deactivated"}


@router.post("/admin/products", status_code=201)
def create_product(
    data: ProductIn, db: Session = Depends(get_db), _=Depends(admin_user)
):
    if not db.get(Category, data.category_id):
        raise HTTPException(404, "Category not found")
    fields = data.model_dump(exclude={"variants"})
    p = Product(**fields)
    db.add(p)
    db.flush()
    db.add_all(
        [ProductVariant(product_id=p.id, **v.model_dump()) for v in data.variants]
    )
    db.commit()
    return {"id": p.id}


@router.put("/admin/products/{product_id}")
def update_product(
    product_id: int,
    data: ProductIn,
    db: Session = Depends(get_db),
    _=Depends(admin_user),
):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    for key, value in data.model_dump(exclude={"variants"}).items():
        setattr(p, key, value)
    db.query(ProductVariant).filter_by(product_id=p.id).delete()
    db.add_all(
        [ProductVariant(product_id=p.id, **v.model_dump()) for v in data.variants]
    )
    db.commit()
    return {"id": p.id}


@router.delete("/admin/products/{product_id}")
def deactivate_product(
    product_id: int, db: Session = Depends(get_db), _=Depends(admin_user)
):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    p.status = False
    db.commit()
    return {"message": "Product deactivated"}
