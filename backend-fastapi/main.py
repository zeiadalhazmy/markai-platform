import os
from typing import Optional, Any, Dict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, MetaData, Table, select, insert
from sqlalchemy.engine import Engine
from jose import jwt  # ✅ بدل import jwt

from app.api import router as api_router

app = FastAPI(title="MarkAi Core API", version="1.0.0")

# CORS
cors = os.environ.get("CORS_ORIGINS", "*")
origins = ["*"] if cors.strip() == "*" else [o.strip() for o in cors.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MarkAi API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Router القديم (health-db وغيره)
app.include_router(api_router)

# DB + JWT
DATABASE_URL = os.getenv("DATABASE_URL", "")
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)
meta = MetaData(schema="public")

# Reflect tables
categories = Table("categories", meta, autoload_with=engine)
delivery_addresses = Table("delivery_addresses", meta, autoload_with=engine)
service_requests = Table("service_requests", meta, autoload_with=engine)

def get_user_id_from_auth(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET missing")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing sub")
    return user_id

# ✅ NEW ENDPOINTS
@app.get("/v1/categories")
def list_categories():
    with engine.begin() as conn:
        rows = conn.execute(select(categories).order_by(categories.c.name.asc())).fetchall()
        return [dict(r._mapping) for r in rows]

@app.post("/v1/addresses")
def create_address(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)

    payload = {
        "user_id": user_id,
        "label": body.get("label"),
        "city": body.get("city"),
        "area": body.get("area"),
        "street": body.get("street"),
        "building": body.get("building"),
        "notes": body.get("notes"),
        "lat": body.get("lat"),
        "lng": body.get("lng"),
        "is_default": bool(body.get("is_default", False)),
    }

    with engine.begin() as conn:
        res = conn.execute(
            insert(delivery_addresses).values(**payload).returning(delivery_addresses.c.id)
        ).first()
        return {"id": str(res[0])}

@app.post("/v1/service-requests")
def create_service_request(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)

    payload = {
        "customer_id": user_id,
        "address_id": body.get("address_id"),
        "vendor_branch_id": body.get("vendor_branch_id"),
        "service_type": body.get("service_type", "water_truck"),
        "status": body.get("status", "pending"),
        "details": body.get("details", {}),
        "scheduled_at": body.get("scheduled_at"),
        "quoted_price": body.get("quoted_price"),
    }

    with engine.begin() as conn:
        res = conn.execute(
            insert(service_requests).values(**payload).returning(service_requests.c.id)
        ).first()
        return {"id": str(res[0])}

@app.get("/v1/service-requests/me")
def my_service_requests(
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)

    with engine.begin() as conn:
        rows = conn.execute(
            select(service_requests)
            .where(service_requests.c.customer_id == user_id)
            .order_by(service_requests.c.created_at.desc())
            .limit(50)
        ).fetchall()
        return [dict(r._mapping) for r in rows]
