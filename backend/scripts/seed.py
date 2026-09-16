"""Run after migrations: python -m scripts.seed (from backend)."""

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User, Role, Category, Product, ProductVariant, Cart


def main():
    db = SessionLocal()
    if db.query(User).filter_by(email="admin@threadline.test").first():
        return
    admin = User(
        name="Store Admin",
        email="admin@threadline.test",
        password_hash=hash_password("AdminPass123!"),
        role=Role.ADMIN,
    )
    customer = User(
        name="Jordan Reed",
        email="jordan@example.test",
        password_hash=hash_password("CustomerPass123!"),
    )
    db.add_all([admin, customer])
    db.flush()
    db.add_all([Cart(user_id=admin.id), Cart(user_id=customer.id)])
    tees = Category(name="T-Shirts", slug="t-shirts")
    outer = Category(name="Jackets", slug="jackets")
    db.add_all([tees, outer])
    db.flush()
    data = [
        (
            "Heavyweight Pocket Tee",
            "heavyweight-pocket-tee",
            tees,
            "Northline",
            "Men",
            1299,
        ),
        ("Everyday Crew Tee", "everyday-crew-tee", tees, "Threadline", "Women", 1099),
        ("Field Overshirt", "field-overshirt", outer, "Northline", "Unisex", 3499),
        (
            "Quilted Liner Jacket",
            "quilted-liner-jacket",
            outer,
            "Threadline",
            "Women",
            4999,
        ),
    ]
    for n, slug, c, b, g, price in data:
        p = Product(
            name=n,
            slug=slug,
            description=f"A considered {n.lower()} made for repeat wear.",
            price=price,
            brand=b,
            gender=g,
            category_id=c.id,
            image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800",
        )
        db.add(p)
        db.flush()
        for color in ("Black", "Natural"):
            for size in ("S", "M", "L"):
                db.add(
                    ProductVariant(
                        product_id=p.id,
                        size=size,
                        color=color,
                        sku=f"{slug[:6]}-{color[0]}-{size}",
                        stock_quantity=25,
                    )
                )
    db.commit()
    print("Seeded admin@threadline.test / AdminPass123!")


if __name__ == "__main__":
    main()
