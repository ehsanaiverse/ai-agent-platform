from fastapi import APIRouter

from app.api.routers.health import router as health_router
from app.api.routers.webhook import router as webhook_router
from app.api.routers.chat import router as chat_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(webhook_router)
api_router.include_router(chat_router)