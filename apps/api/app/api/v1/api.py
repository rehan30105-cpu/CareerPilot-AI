"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import analyses, auth, health, resumes

api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(resumes.router)
api_router.include_router(analyses.router)

