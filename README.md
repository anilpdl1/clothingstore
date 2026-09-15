# Threadline — Full-stack clothing commerce

A responsive React/Tailwind clothing store backed by FastAPI, SQLAlchemy/MySQL and eSewa. It includes role-secured customer and admin flows, variant inventory, a persistent cart, checkout, order history and a store dashboard.

It also includes verified purchase reviews/ratings, moderation, helpful votes/reports, interaction tracking, and a content/co-occurrence recommendation system with cold-start fallbacks.

## Quick start

Copy `.env.example` to `.env`, configure MySQL/eSewa, then run:

```bash
docker compose up --build
```

Compose waits for MySQL and applies Alembic migrations before starting FastAPI. For local processes, run `alembic upgrade head` from `backend` before starting the API.

Open `http://localhost:5173`; API docs are at `http://localhost:8000/docs`. Seed with `python -m scripts.seed` from `backend`. Development admin: `admin@threadline.test` / `AdminPass123!` (change/remove outside development).

## Payment flow

FastAPI locks and validates cart stock, recalculates totals, and creates a server-signed eSewa ePay V2 form. The browser posts that form to eSewa. FastAPI verifies eSewa's signed response and status before decrementing inventory, confirming the order, and clearing the cart.

See [setup](docs/SETUP.md), [architecture](docs/ARCHITECTURE.md), [database](docs/DATABASE.md), and [API reference](docs/API_DOCUMENTATION.md).
