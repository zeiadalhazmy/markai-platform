import os
from typing import Optional, Any, Dict

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, insert, inspect, Table
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api import router as api_router
from app.core_app.config import settings
from app.core_app.security import get_user_id_from_auth
from app.infrastructure.db import (
    engine,
    categories, addresses, service_requests,
    vendors, vendor_branches, products, product_images, branch_inventory,
    orders, order_items, user_roles, couriers, profiles
)


SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hcakrxaaarkufkxrehwy.supabase.co")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

_jwks_cache = None

app = FastAPI(title="MarkAi Core API", version="1.0.0")

origins = settings.cors_origins_list


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

@app.get("/v1/me")
def me(authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    roles = sorted(list(get_user_roles(user_id)))
    return {"user_id": user_id, "roles": roles}


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
def create_address(body: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)

    raw = {
        "user_id": user_id,
        "label": body.get("label"),
        "city": body.get("city"),

        # area/district
        "area": body.get("area") or body.get("district"),
        "district": body.get("district") or body.get("area"),

        "street": body.get("street"),
        "building": body.get("building"),

        # notes/landmark
        "notes": body.get("notes") or body.get("landmark"),
        "landmark": body.get("landmark") or body.get("notes"),

        # lat/lng OR latitude/longitude
        "lat": body.get("lat") or body.get("latitude"),
        "latitude": body.get("latitude") or body.get("lat"),
        "lng": body.get("lng") or body.get("longitude"),
        "longitude": body.get("longitude") or body.get("lng"),

        "is_default": bool(body.get("is_default", False)),
    }

    payload = only_existing_cols(addresses, raw)

    with engine.begin() as conn:
        res = conn.execute(insert(addresses).values(**payload).returning(addresses.c.id)).first()
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

def pick_col(tbl: Table, candidates: list[str], required: bool = True) -> Optional[str]:
    for c in candidates:
        if c in tbl.c:
            return c
    if required:
        raise HTTPException(
            status_code=500,
            detail=f"DB schema mismatch: {tbl.name} missing one of {candidates}"
        )
    return None

def set_if_col(payload: Dict[str, Any], tbl: Table, candidates: list[str], value: Any) -> Optional[str]:
    for c in candidates:
        if c in tbl.c:
            payload[c] = value
            return c
    return None



@app.post("/v1/orders")
def create_order(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)

    items = body.get("items", [])
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="items is required")

    vendor_branch_id = body.get("vendor_branch_id")
    address_id = body.get("address_id")
    if not vendor_branch_id:
        raise HTTPException(status_code=400, detail="vendor_branch_id is required")

    # orders columns
    customer_col = pick_col(orders, ["customer_user_id", "customer_id", "user_id", "profile_id"])
    branch_col   = pick_col(orders, ["vendor_branch_id", "branch_id"])
    status_col   = pick_col(orders, ["status"], required=False)
    total_col    = pick_col(orders, ["total", "total_amount", "total_price", "amount_total"], required=False)
    type_col     = pick_col(orders, ["type", "order_type", "kind"], required=False)
    currency_col = pick_col(orders, ["currency"], required=False)
    notes_col    = pick_col(orders, ["notes", "note"], required=False)
    address_col  = pick_col(orders, ["address_id", "delivery_address_id", "customer_address_id"], required=False)

    # order_items columns
    oi_order_col      = pick_col(order_items, ["order_id"])
    oi_product_col    = pick_col(order_items, ["product_id"])
    oi_qty_col        = pick_col(order_items, ["quantity", "qty", "count"])
    oi_unit_price_col = pick_col(order_items, ["unit_price", "price"], required=False)
    oi_total_col      = pick_col(order_items, ["total", "line_total", "total_price", "amount"], required=False)

    # snapshot columns
    oi_name_snap_col  = pick_col(order_items, ["name_snapshot", "product_name_snapshot", "title_snapshot"], required=False)
    oi_price_snap_col = pick_col(order_items, ["price_snapshot", "unit_price_snapshot"], required=False)
    oi_currency_col   = pick_col(order_items, ["currency"], required=False)
    oi_image_snap_col = pick_col(order_items, ["image_snapshot", "image_url_snapshot", "thumbnail_snapshot"], required=False)
    oi_snapshot_col   = pick_col(order_items, ["product_snapshot", "item_snapshot", "snapshot"], required=False)

    # product fields
    prod_name_col = pick_col(products, ["name", "title"], required=False)
    img_url_col   = pick_col(product_images, ["url", "image_url", "src"], required=False)

    try:
        with engine.begin() as conn:
            vb = conn.execute(
                select(vendor_branches.c.vendor_id)
                .where(vendor_branches.c.id == vendor_branch_id)
                .limit(1)
            ).first()
            if not vb or not vb[0]:
                raise HTTPException(status_code=400, detail="vendor_branch_id not found")
            vendor_id = str(vb[0])

            order_payload: Dict[str, Any] = {
                customer_col: user_id,
                branch_col: vendor_branch_id,
            }

            set_if_col(order_payload, orders, ["vendor_id", "store_id"], vendor_id)

            # ✅ address fk check (validate before insert) - مرة واحدة فقط
            if address_col and address_id:
                a = conn.execute(
                    select(addresses.c.id).where(addresses.c.id == address_id).limit(1)
                ).first()
                if not a:
                    raise HTTPException(
                        status_code=400,
                        detail=f"address_id not found in {addresses.name}"
                    )
                order_payload[address_col] = address_id

            if status_col:
                order_payload[status_col] = body.get("status") or "placed"
            if type_col:
                order_payload[type_col] = body.get("type") or "water_truck"
            if total_col:
                order_payload[total_col] = 0
            if currency_col:
                order_payload[currency_col] = "YER"
            if notes_col and body.get("notes") is not None:
                order_payload[notes_col] = body.get("notes")

            new_order = conn.execute(
                insert(orders).values(**order_payload).returning(orders.c.id)
            ).first()
            order_id = new_order[0]

            inv_price_col  = pick_col(branch_inventory, ["price_override", "price", "unit_price"], required=False)
            prod_price_col = pick_col(products, ["price"], required=False)

            total = 0.0

            for it in items:
                product_id = it.get("product_id")
                qty = int(it.get("quantity", 1) or 1)
                if not product_id:
                    raise HTTPException(status_code=400, detail="product_id missing in items")

                unit_price = 0.0

                inv_row = conn.execute(
                    select(branch_inventory)
                    .where(branch_inventory.c.branch_id == vendor_branch_id)
                    .where(branch_inventory.c.product_id == product_id)
                    .limit(1)
                ).first()

                if inv_row and inv_price_col:
                    invd = dict(inv_row._mapping)
                    unit_price = float(invd.get(inv_price_col) or 0)

                if unit_price == 0 and prod_price_col:
                    pr = conn.execute(
                        select(getattr(products.c, prod_price_col))
                        .where(products.c.id == product_id)
                        .limit(1)
                    ).first()
                    if pr and pr[0] is not None:
                        unit_price = float(pr[0])

                line_total = unit_price * qty
                total += line_total

                item_payload: Dict[str, Any] = {
                    oi_order_col: order_id,
                    oi_product_col: product_id,
                    oi_qty_col: qty,
                }

                set_if_col(item_payload, order_items, ["vendor_branch_id", "branch_id"], vendor_branch_id)
                set_if_col(item_payload, order_items, ["vendor_id", "store_id"], vendor_id)

                if oi_unit_price_col:
                    item_payload[oi_unit_price_col] = unit_price
                if oi_total_col:
                    item_payload[oi_total_col] = line_total

                product_name = None
                if prod_name_col:
                    prn = conn.execute(
                        select(getattr(products.c, prod_name_col))
                        .where(products.c.id == product_id)
                        .limit(1)
                    ).first()
                    if prn and prn[0] is not None:
                        product_name = str(prn[0])
                if not product_name:
                    product_name = "Product"

                image_url = ""
                if img_url_col:
                    ir = conn.execute(
                        select(getattr(product_images.c, img_url_col))
                        .where(product_images.c.product_id == product_id)
                        .limit(1)
                    ).first()
                    if ir and ir[0] is not None:
                        image_url = str(ir[0])

                if oi_name_snap_col:
                    item_payload[oi_name_snap_col] = product_name
                if oi_price_snap_col:
                    item_payload[oi_price_snap_col] = unit_price
                if oi_currency_col:
                    item_payload[oi_currency_col] = "YER"
                if oi_image_snap_col:
                    item_payload[oi_image_snap_col] = image_url
                if oi_snapshot_col:
                    item_payload[oi_snapshot_col] = {
                        "product_id": str(product_id),
                        "name": product_name,
                        "unit_price": unit_price,
                        "qty": qty,
                    }

                conn.execute(insert(order_items).values(**item_payload))

            if total_col:
                conn.execute(
                    orders.update().where(orders.c.id == order_id).values(**{total_col: total})
                )

            return {"id": str(order_id), "total": total}

    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"DB IntegrityError: {str(getattr(e, 'orig', e))}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")






@app.get("/v1/orders/me")
def my_orders(authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    customer_col = pick_col(orders, ["customer_user_id", "customer_id", "user_id", "profile_id"])

    with engine.begin() as conn:
        stmt = (
            select(orders)
            .where(getattr(orders.c, customer_col) == user_id)
            .order_by(orders.c.created_at.desc())
            .limit(50)
        )
        rows = conn.execute(stmt).fetchall()
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

    # عرّف customer_col دائمًا (حتى admin/merchant)
    customer_col = pick_col(orders, ["customer_user_id", "customer_id", "user_id", "profile_id"])

    with engine.begin() as conn:
        order_row = conn.execute(
            select(orders).where(orders.c.id == order_id).limit(1)
        ).first()
        if not order_row:
            raise HTTPException(status_code=404, detail="order not found")

        order_dict = dict(order_row._mapping)

        # العميل يشوف طلبه فقط
        if "admin" not in roles and "merchant" not in roles:
            if str(order_dict.get(customer_col)) != str(user_id):
                raise HTTPException(status_code=403, detail="not allowed")

        items = conn.execute(
            select(order_items).where(order_items.c.order_id == order_id)
        ).fetchall()
        items_list = [dict(r._mapping) for r in items]

        return {"order": order_dict, "items": items_list}


@app.patch("/v1/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="status is required")

    allowed = {
    "draft",
    "placed",
    "accepted",
    "preparing",
    "ready",
    "assigned",
    "picked_up",
    "en_route",
    "delivered",
    "cancelled",
    "refunded",
              }
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

# =========================
# Vendor Admin CRUD
# =========================

def _best_owner_col(tbl: Table) -> Optional[str]:
    # أسماء أعمدة المالك المحتملة (حسب سكيمتك)
    for c in ["owner_user_id", "owner_id", "user_id", "profile_id", "created_by"]:
        if c in tbl.c:
            return c
    return None



def _order_col(tbl: Table) -> Any:
    # ترتيب آمن بدون افتراض أعمدة
    if "created_at" in tbl.c:
        return tbl.c.created_at.desc()
    if "updated_at" in tbl.c:
        return tbl.c.updated_at.desc()
    return tbl.c.id.desc()

def _owned_vendor_ids(conn, user_id: str) -> list[str]:
    owner_col = _best_owner_col(vendors)
    if not owner_col:
        # إذا جدول vendors ما فيه owner_id/user_id... نرجع كل شيء (حل مؤقت)
        rows = conn.execute(select(vendors.c.id)).fetchall()
        return [str(r[0]) for r in rows]

    rows = conn.execute(
        select(vendors.c.id).where(getattr(vendors.c, owner_col) == user_id)
    ).fetchall()
    return [str(r[0]) for r in rows]

def _assert_vendor_owned(conn, vendor_id: str, user_id: str):
    ids = _owned_vendor_ids(conn, user_id)
    if vendor_id not in ids:
        raise HTTPException(status_code=403, detail="vendor not owned by you")

def _assert_branch_owned(conn, branch_id: str, user_id: str) -> str:
    # يرجّع vendor_id الخاص بالفرع بعد التحقق
    row = conn.execute(
        select(vendor_branches).where(vendor_branches.c.id == branch_id).limit(1)
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="branch not found")

    b = dict(row._mapping)
    vid = str(b.get("vendor_id")) if b.get("vendor_id") else None
    if not vid:
        raise HTTPException(status_code=400, detail="branch missing vendor_id")

    _assert_vendor_owned(conn, vid, user_id)
    return vid

@app.get("/v1/vendor-admin/me")
def vendor_admin_me(authorization: Optional[str] = Header(default=None)):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        vids = _owned_vendor_ids(conn, user_id)
        return {"user_id": user_id, "vendor_ids": vids}

# 1) Vendors
@app.post("/v1/vendor-admin/vendors")
def create_vendor_admin_vendor(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    payload = dict(body)

    # ثبت المالك لو العمود موجود
    owner_col = _best_owner_col(vendors)
    if owner_col and owner_col not in payload:
        payload[owner_col] = user_id

    payload = only_existing_cols(vendors, payload)

    with engine.begin() as conn:
        res = conn.execute(insert(vendors).values(**payload).returning(vendors.c.id)).first()
        return {"id": str(res[0])}

@app.patch("/v1/vendor-admin/vendors/{vendor_id}")
def update_vendor_admin_vendor(
    vendor_id: str,
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        _assert_vendor_owned(conn, vendor_id, user_id)

        payload = only_existing_cols(vendors, body)
        if not payload:
            return {"ok": True}

        conn.execute(vendors.update().where(vendors.c.id == vendor_id).values(**payload))
        return {"ok": True}

@app.get("/v1/vendor-admin/vendors")
def list_my_vendors(
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        owner_col = _best_owner_col(vendors)
        stmt = select(vendors)
        if owner_col:
            stmt = stmt.where(getattr(vendors.c, owner_col) == user_id)
        rows = conn.execute(stmt.order_by(_order_col(vendors))).fetchall()
        return [dict(r._mapping) for r in rows]

# 2) Branches
@app.post("/v1/vendor-admin/branches")
def create_branch(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    vendor_id = body.get("vendor_id")
    if not vendor_id:
        raise HTTPException(status_code=400, detail="vendor_id is required")

    with engine.begin() as conn:
        _assert_vendor_owned(conn, str(vendor_id), user_id)

        payload = only_existing_cols(vendor_branches, body)
        res = conn.execute(
            insert(vendor_branches).values(**payload).returning(vendor_branches.c.id)
        ).first()
        return {"id": str(res[0])}

@app.patch("/v1/vendor-admin/branches/{branch_id}")
def update_branch(
    branch_id: str,
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        _assert_branch_owned(conn, branch_id, user_id)

        payload = only_existing_cols(vendor_branches, body)
        if not payload:
            return {"ok": True}

        conn.execute(vendor_branches.update().where(vendor_branches.c.id == branch_id).values(**payload))
        return {"ok": True}

@app.get("/v1/vendor-admin/branches")
def list_my_branches(
    vendor_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        stmt = select(vendor_branches)

        if vendor_id:
            _assert_vendor_owned(conn, vendor_id, user_id)
            stmt = stmt.where(vendor_branches.c.vendor_id == vendor_id)
        else:
            vids = _owned_vendor_ids(conn, user_id)
            if vids:
                stmt = stmt.where(vendor_branches.c.vendor_id.in_(vids))
            else:
                return []

        rows = conn.execute(stmt.order_by(_order_col(vendor_branches))).fetchall()
        return [dict(r._mapping) for r in rows]

# 3) Products
@app.post("/v1/vendor-admin/products")
def create_product(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    # المنتج غالبًا مرتبط بـ vendor_id (لو موجود) أو نربطه بفرع عبر inventory
    with engine.begin() as conn:
        # لو أرسل vendor_id تحقق الملكية
        if "vendor_id" in body and body.get("vendor_id"):
            _assert_vendor_owned(conn, str(body["vendor_id"]), user_id)

        payload = only_existing_cols(products, body)
        res = conn.execute(insert(products).values(**payload).returning(products.c.id)).first()
        return {"id": str(res[0])}

@app.patch("/v1/vendor-admin/products/{product_id}")
def update_product(
    product_id: str,
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        # لو جدول products فيه vendor_id نتحقق الملكية
        if "vendor_id" in products.c:
            row = conn.execute(select(products).where(products.c.id == product_id).limit(1)).first()
            if not row:
                raise HTTPException(status_code=404, detail="product not found")
            p = dict(row._mapping)
            vid = p.get("vendor_id")
            if vid:
                _assert_vendor_owned(conn, str(vid), user_id)

        payload = only_existing_cols(products, body)
        if not payload:
            return {"ok": True}

        conn.execute(products.update().where(products.c.id == product_id).values(**payload))
        return {"ok": True}

@app.get("/v1/vendor-admin/products")
def list_my_products(
    vendor_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    with engine.begin() as conn:
        stmt = select(products)

        if vendor_id and "vendor_id" in products.c:
            _assert_vendor_owned(conn, vendor_id, user_id)
            stmt = stmt.where(products.c.vendor_id == vendor_id)
        elif "vendor_id" in products.c:
            vids = _owned_vendor_ids(conn, user_id)
            if vids:
                stmt = stmt.where(products.c.vendor_id.in_(vids))
            else:
                return []

        rows = conn.execute(stmt.order_by(_order_col(products)).limit(200)).fetchall()
        return [dict(r._mapping) for r in rows]

# 4) Product Images (روابط صور)
@app.post("/v1/vendor-admin/products/{product_id}/images")
def add_product_image(
    product_id: str,
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    image_url = body.get("url") or body.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="url is required")

    with engine.begin() as conn:
        # تحقق ملكية المنتج لو فيه vendor_id
        if "vendor_id" in products.c:
            row = conn.execute(select(products).where(products.c.id == product_id).limit(1)).first()
            if not row:
                raise HTTPException(status_code=404, detail="product not found")
            p = dict(row._mapping)
            vid = p.get("vendor_id")
            if vid:
                _assert_vendor_owned(conn, str(vid), user_id)

        payload = {"product_id": product_id, "url": image_url}
        payload = only_existing_cols(product_images, payload)

        res = conn.execute(insert(product_images).values(**payload).returning(product_images.c.id)).first()
        return {"id": str(res[0])}

# 5) Inventory Upsert (فرع + منتج)
@app.put("/v1/vendor-admin/inventory")
def upsert_inventory(
    body: Dict[str, Any],
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    require_any_role(user_id, ["admin", "merchant"])

    branch_id = body.get("branch_id")
    product_id = body.get("product_id")
    if not branch_id or not product_id:
        raise HTTPException(status_code=400, detail="branch_id and product_id are required")

    with engine.begin() as conn:
        _assert_branch_owned(conn, str(branch_id), user_id)

        # هل موجود؟
        existing = conn.execute(
            select(branch_inventory)
            .where(branch_inventory.c.branch_id == branch_id)
            .where(branch_inventory.c.product_id == product_id)
            .limit(1)
        ).first()

        payload = only_existing_cols(branch_inventory, body)

        if existing:
            conn.execute(
                branch_inventory.update()
                .where(branch_inventory.c.branch_id == branch_id)
                .where(branch_inventory.c.product_id == product_id)
                .values(**payload)
            )
            return {"ok": True, "mode": "updated"}

        res = conn.execute(insert(branch_inventory).values(**payload).returning(branch_inventory.c.id)).first()
        return {"ok": True, "mode": "inserted", "id": str(res[0])}

@app.get("/v1/vendor-admin/orders")
def vendor_orders(
    vendor_id: Optional[str] = Query(default=None),
    branch_id: Optional[str] = Query(default=None),
    authorization: Optional[str] = Header(default=None),
):
    user_id = get_user_id_from_auth(authorization)
    roles = get_user_roles(user_id)
    require_any_role(user_id, ["admin", "merchant"])

    is_admin = "admin" in roles

    # detect columns safely
    branch_col = "vendor_branch_id" if "vendor_branch_id" in orders.c else ("branch_id" if "branch_id" in orders.c else None)
    vendor_col = "vendor_id" if "vendor_id" in orders.c else None

    with engine.begin() as conn:
        stmt = select(orders)

        if is_admin:
            # admin: اختياري فلترة
            if vendor_id and vendor_col:
                stmt = stmt.where(getattr(orders.c, vendor_col) == vendor_id)

            if branch_id and branch_col:
                stmt = stmt.where(getattr(orders.c, branch_col) == branch_id)

        else:
            # merchant: لازم يكون عنده vendors
            vids = _owned_vendor_ids(conn, user_id)
            if not vids:
                return []

            if vendor_id:
                _assert_vendor_owned(conn, vendor_id, user_id)
                vids = [vendor_id]

            if vendor_col:
                stmt = stmt.where(getattr(orders.c, vendor_col).in_(vids))
            else:
                raise HTTPException(status_code=500, detail="orders table missing vendor_id; cannot scope merchant orders safely")

            if branch_id and branch_col:
                _assert_branch_owned(conn, branch_id, user_id)
                stmt = stmt.where(getattr(orders.c, branch_col) == branch_id)

        rows = conn.execute(stmt.order_by(_order_col(orders)).limit(100)).fetchall()
        return [dict(r._mapping) for r in rows]


# Router القديم (health-db وغيره)
app.include_router(api_router)
