from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .db import get_db

router = APIRouter(prefix="/v1")

@router.get("/health-db")
def health_db(db: Session = Depends(get_db)):
    db.execute("select 1")
    return {"db": "ok"}
