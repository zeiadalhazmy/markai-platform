from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api import router


app.include_router(router)
app = FastAPI(title="MarkAi Core API", version="1.0.0")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok"}
