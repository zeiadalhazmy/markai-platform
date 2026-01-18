import os
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.engine import Engine
from fastapi import HTTPException

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)
meta = MetaData(schema="public")

def reflect_table(name: str) -> Table:
    return Table(name, meta, autoload_with=engine)

insp = inspect(engine)

categories = reflect_table("categories")

ADDRESS_TABLE = "delivery_addresses" if insp.has_table("delivery_addresses", schema="public") else "addresses"
addresses = reflect_table(ADDRESS_TABLE)

service_requests = reflect_table("service_requests")
vendors = reflect_table("vendors")
vendor_branches = reflect_table("vendor_branches")
products = reflect_table("products")
product_images = reflect_table("product_images")
branch_inventory = reflect_table("branch_inventory")
orders = reflect_table("orders")
order_items = reflect_table("order_items")
user_roles = reflect_table("user_roles")
couriers = reflect_table("couriers")
profiles = reflect_table("profiles")
