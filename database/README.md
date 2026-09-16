# Database migrations

Alembic is already initialized in `backend/alembic`. The repository-level
`.env` supplies `DATABASE_URL`; do not add a URL to `alembic.ini` and do not
run `alembic init` again. For a new database, run:

```bash
alembic upgrade head
```

The SQLAlchemy models are the canonical normalized schema and expose foreign keys, unique cart/variant and product/option constraints, plus catalogue and stock indexes. The initial revision creates every table, including reviews, moderation, interactions, recommendations, carts, orders and payments.
