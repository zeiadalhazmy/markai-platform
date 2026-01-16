from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import router

app = FastAPI(title="MarkAi Core API", version="1.0.0")

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

app.include_router(router)
