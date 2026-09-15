from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth,catalog,cart,payments,orders,admin,reviews,recommendations
app=FastAPI(title="Threadline Commerce API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_url],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for route in (auth.router,catalog.router,cart.router,payments.router,orders.router,admin.router,reviews.router,recommendations.router):app.include_router(route)
@app.get("/health")
def health():return {"status":"ok"}
