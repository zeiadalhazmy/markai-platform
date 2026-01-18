from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/")
def root():
    return {"message": "MarkAi API", "docs": "/docs"}
