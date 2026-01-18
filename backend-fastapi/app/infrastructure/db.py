from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.engine import Engine

from app.core_app.config import settings

if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

engine: Engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
meta = MetaData(schema="public")

# Reflect tables
categories = Table("categories", meta, autoload_with=engine)

insp = inspect(engine)
ADDRESS_TABLE = "delivery_addresses" if insp.has_table("delivery_addresses", schema="public") else "addresses"
addresses = Table(ADDRESS_TABLE, meta, autoload_with=engine)

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
