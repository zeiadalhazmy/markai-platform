from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import get_db

router = APIRouter(prefix="/v1")

@router.get("/health-db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("select 1"))
    return {"db": "ok"}
