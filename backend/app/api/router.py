from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.posts import router as posts_router
from app.api.calendar import router as calendar_router
from app.api.agent import router as agent_router
from app.api.uploads import router as uploads_router
from app.api.settings import router as settings_router
from app.api.typefully import router as typefully_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(posts_router)
api_router.include_router(calendar_router)
api_router.include_router(agent_router)
api_router.include_router(uploads_router)
api_router.include_router(settings_router)
api_router.include_router(typefully_router)
