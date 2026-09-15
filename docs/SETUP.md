# Setup

1. Copy `.env.example` to `.env` and set a strong `SECRET_KEY` plus eSewa test/live credentials. Set `BACKEND_PUBLIC_URL` to a publicly reachable HTTPS backend URL before a real eSewa payment; eSewa cannot redirect to localhost.
2. Start MySQL and run `docker compose up --build` (Compose waits for MySQL, applies `alembic upgrade head`, then starts the API). For separate local processes, run `alembic upgrade head && python -m uvicorn app.main:app --reload` from `backend`, then `npm install && npm run dev` from `frontend`.
3. Run `python -m scripts.seed` from `backend` after MySQL is available.

Use eSewa UAT credentials initially. The eSewa secret key stays in FastAPI; the browser only receives a server-signed payment form.
