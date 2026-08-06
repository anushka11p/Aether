from fastapi import FastAPI
from app.api.routes import router
from app.api.websocket import router as ws_router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router, prefix="/api")
app.include_router(ws_router)

@app.get("/")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}