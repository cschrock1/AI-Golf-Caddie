from fastapi import APIRouter

from app.api.routes import health
from app.routes.clubs import router as clubs_router
from app.routes.courses import router as courses_router
from app.routes.golfer import router as golfer_router
from app.routes.rounds import router as rounds_router
from app.routes.shots import router as shots_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, tags=["health"], prefix="")
api_router.include_router(clubs_router)
api_router.include_router(courses_router)
api_router.include_router(golfer_router)
api_router.include_router(rounds_router)
api_router.include_router(shots_router)
