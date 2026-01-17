import os
from fastapi import Query
from typing import Optional, Any, Dict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, MetaData, Table, select, insert, inspect
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

vendors = Table("vendors", meta, autoload_with=engine)
vendor_branches = Table("vendor_branches", meta, autoload_with=engine)
products = Table("products", meta, autoload_with=engine)
product_images = Table("product_images", meta, autoload_with=engine)
branch_inventory = Table("branch_inventory", meta, autoload_with=engine)
orders = Table("orders", meta, autoload_with=engine)
order_items = Table("order_items", meta, autoload_with=engine)
user_roles = Table("user_roles", meta, autoload_with=engine)
couriers = Table("couriers", meta, autoload_with=engine)
profiles = Table("profiles", meta, autoload_with=engine)



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

def only_existing_cols(table: Table, data: Dict[str, Any]) -> Dict[str, Any]:
    cols = set(table.c.keys())
    return {k: v for k, v in data.items() if k in cols}

def get_user_roles(user_id: str) -> set[str]:
    with engine.begin() as conn:
        # حاول يقرأ من user_roles (role column)
        if "role" in user_roles.c:
            rows = conn.execute(
                select(user_roles.c.role).where(user_roles.c.user_id == user_id)
            ).fetchall()
            return {str(r[0]) for r in rows}
        return set()

def require_any_role(user_id: str, allowed: list[str]):
    roles = get_user_roles(user_id)
    if not roles.intersection(set(allowed)):
        raise HTTPException(status_code=403, detail=f"Requires role in {allowed}")
    return roles

def resolve_courier_id(conn, user_id: str) -> str:
    # نحاول نطلع courier.id من couriers حسب الأعمدة الموجودة
    if "user_id" in couriers.c:
        row = conn.execute(select(couriers.c.id).where(couriers.c.user_id == user_id).limit(1)).first()
        if row:
            return str(row[0])
        # إذا ما موجود، نحاول ننشئ سجل courier تلقائيًا (إذا الجدول يسمح)
        payload = only_existing_cols(couriers, {"user_id": user_id, "is_active": True})
        try:
            new_row = conn.execute(insert(couriers).values(**payload).returning(couriers.c.id)).first()
            return str(new_row[0])
        except Exception:
            raise HTTPException(status_code=400, detail="Courier record missing. Create it in couriers table first.")
    elif "profile_id" in couriers.c:
        row = conn.execute(select(couriers.c.id).where(couriers.c.profile_id == user_id).limit(1)).first()
        if row:
            return str(row[0])
        payload = only_existing_cols(couriers, {"profile_id": user_id, "is_active": True})
        try:
            new_row = conn.execute(insert(couriers).values(**payload).returning(couriers.c.id)).first()
            return str(new_row[0])
        except Exception:
            raise HTTPException(status_code=400, detail="Courier record missing. Create it in couriers table first.")
    else:
        # آخر حل: نفترض id = user_id (لو تصميمك كذا)
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


@app.get("/v1/vendors")
def list_vendors():
    with engine.begin() as conn:
        rows = conn.execute(select(vendors).order_by(vendors.c.created_at.desc())).fetchall()
        return [dict(r._mapping) for r in rows]

@app.get("/v1/vendor-branches")
def list_vendor_branches(
    vendor_id: Optional[str] = Query(default=None),
):
    q = select(vendor_branches)
    if vendor_id:
        q = q.where(vendor_branches.c.vendor_id == vendor_id)

    with engine.begin() as conn:
        rows = conn.execute(q.order_by(vendor_branches.c.created_at.desc())).fetchall()
        return [dict(r._mapping) for r in rows]

@app.get("/v1/products")
def list_products(
    branch_id: Optional[str] = Query(default=None),
    category_id: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    stmt = select(products)

    # فلترة
    if category_id and "category_id" in products.c:
        stmt = stmt.where(products.c.category_id == category_id)

    if q and "name" in products.c:
        stmt = stmt.where(products.c.name.ilike(f"%{q}%"))

    # لو في branch_id: رجّع المخزون والسعر من branch_inventory
    if branch_id:
        stmt = (
            select(
                products,
                branch_inventory.c.quantity.label("branch_quantity"),
                branch_inventory.c.price_override.label("branch_price_override"),
                branch_inventory.c.is_available.label("branch_is_available"),
            )
            .select_from(
                products.join(
                    branch_inventory,
                    (branch_inventory.c.product_id == products.c.id)
                    & (branch_inventory.c.branch_id == branch_id),
                    isouter=True,
                )
            )
        )

    stmt = stmt.limit(limit)

    with engine.begin() as conn:
        rows = conn.execute(stmt).fetchall()

        # تحويل النتائج ل dict
        items = [dict(r._mapping) for r in rows]

        # اجلب الصور
        ids = [str(it.get("id")) for it in items if it.get("id")]
        images_map: Dict[str, list] = {pid: [] for pid in ids}

        if ids:
            img_rows = conn.execute(
                select(product_images).where(product_images.c.product_id.in_(ids))
            ).fetchall()
            for ir in img_rows:
                d = dict(ir._mapping)
                pid = str(d.get("product_id"))
                if pid in images_map:
                    images_map[pid].append(d)

        # ألصق الصور مع المنتج
        for it in items:
            pid = str(it.get("id"))
            it["images"] = images_map.get(pid, [])

        return items

@app.post("/v1/orders")
def create_order(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)

    items = body.get("items", [])
    if not isinstance(items, list) or len(items) == 0:
        raise HTTPException(status_code=400, detail="items is required")

    vendor_branch_id = body.get("vendor_branch_id")
    address_id = body.get("address_id")

    with engine.begin() as conn:
        # نحسب total بشكل بسيط
        total = 0

        # جهز order row حسب الأعمدة الموجودة فعليًا
        order_payload = only_existing_cols(orders, {
            "customer_id": user_id,
            "vendor_branch_id": vendor_branch_id,
            "address_id": address_id,
            "status": "pending",
            "total": 0,  # نحدثه بعد الحساب
            "currency": "YER",
            "notes": body.get("notes"),
        })

        new_order = conn.execute(
            insert(orders).values(**order_payload).returning(orders.c.id)
        ).first()
        order_id = new_order[0]

        # إدخال order_items
        for it in items:
            product_id = it.get("product_id")
            qty = int(it.get("quantity", 1))
            if not product_id:
                raise HTTPException(status_code=400, detail="product_id missing in items")

            # سعر: من branch_inventory إذا موجود، وإلا من products.price لو موجود
            unit_price = 0

            if vendor_branch_id:
                inv = conn.execute(
                    select(branch_inventory)
                    .where(branch_inventory.c.branch_id == vendor_branch_id)
                    .where(branch_inventory.c.product_id == product_id)
                    .limit(1)
                ).first()
                if inv:
                    invd = dict(inv._mapping)
                    unit_price = invd.get("price_override") or 0

            if unit_price == 0 and "price" in products.c:
                pr = conn.execute(
                    select(products.c.price).where(products.c.id == product_id).limit(1)
                ).first()
                if pr and pr[0] is not None:
                    unit_price = pr[0]

            line_total = float(unit_price) * qty
            total += line_total

            item_payload = only_existing_cols(order_items, {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": qty,
                "unit_price": unit_price,
                "total": line_total,
            })

            conn.execute(insert(order_items).values(**item_payload))

        # تحديث total في orders لو العمود موجود
        if "total" in orders.c:
            conn.execute(
                orders.update().where(orders.c.id == order_id).values(total=total)
            )

        return {"id": str(order_id), "total": total}


@app.get("/v1/orders/me")
def my_orders(
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)

    with engine.begin() as conn:
        rows = conn.execute(
            select(orders)
            .where(orders.c.customer_id == user_id)
            .order_by(orders.c.created_at.desc())
            .limit(50)
        ).fetchall()
        return [dict(r._mapping) for r in rows]

@app.get("/v1/_schema/{table_name}")
def table_schema(table_name: str):
    insp = inspect(engine)
    try:
        cols = insp.get_columns(table_name, schema="public")
    except Exception:
        raise HTTPException(status_code=404, detail="table not found")
    return [
        {
            "name": c["name"],
            "type": str(c["type"]),
            "nullable": c.get("nullable", True),
            "default": str(c.get("default")),
        }
        for c in cols
    ]

@app.get("/v1/orders/{order_id}")
def order_details(order_id: str, authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    roles = get_user_roles(user_id)

    with engine.begin() as conn:
        order_row = conn.execute(select(orders).where(orders.c.id == order_id).limit(1)).first()
        if not order_row:
            raise HTTPException(status_code=404, detail="order not found")

        order_dict = dict(order_row._mapping)

        # العميل يشوف طلبه فقط
        if "admin" not in roles and "vendor_admin" not in roles:
            if str(order_dict.get("customer_id")) != str(user_id):
                raise HTTPException(status_code=403, detail="not allowed")

        items = conn.execute(select(order_items).where(order_items.c.order_id == order_id)).fetchall()
        items_list = [dict(r._mapping) for r in items]

        return {"order": order_dict, "items": items_list}


@app.patch("/v1/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "vendor_admin"])

    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="status is required")

    allowed = {"pending", "accepted", "preparing", "out_for_delivery", "delivered", "cancelled"}
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"invalid status. allowed: {sorted(list(allowed))}")

    with engine.begin() as conn:
        res = conn.execute(
            orders.update().where(orders.c.id == order_id).values(status=new_status)
        )
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="order not found")
        return {"ok": True, "status": new_status}

@app.get("/v1/service-requests/available")
def available_service_requests(authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "courier"])

    with engine.begin() as conn:
        stmt = select(service_requests).where(service_requests.c.status == "pending").order_by(service_requests.c.created_at.desc()).limit(50)
        rows = conn.execute(stmt).fetchall()
        return [dict(r._mapping) for r in rows]


@app.post("/v1/service-requests/{req_id}/accept")
def accept_service_request(req_id: str, authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "courier"])

    with engine.begin() as conn:
        courier_id = resolve_courier_id(conn, user_id)

        # نقبل فقط إذا still pending
        res = conn.execute(
            service_requests.update()
            .where(service_requests.c.id == req_id)
            .where(service_requests.c.status == "pending")
            .values(status="accepted", courier_id=courier_id)
        )
        if res.rowcount == 0:
            raise HTTPException(status_code=400, detail="request not found or not pending")
        return {"ok": True, "status": "accepted"}


@app.post("/v1/service-requests/{req_id}/complete")
def complete_service_request(req_id: str, authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "courier"])

    with engine.begin() as conn:
        courier_id = resolve_courier_id(conn, user_id)

        res = conn.execute(
            service_requests.update()
            .where(service_requests.c.id == req_id)
            .where(service_requests.c.courier_id == courier_id)
            .values(status="completed")
        )
        if res.rowcount == 0:
            raise HTTPException(status_code=400, detail="not allowed or not found")
        return {"ok": True, "status": "completed"}
