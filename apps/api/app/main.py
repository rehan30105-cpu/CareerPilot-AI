"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("main")

app = FastAPI(
    title=settings.app_name,
    description="AI-powered career intelligence platform",
    version="0.1.0",
    debug=settings.app_debug,
)

# CORS — restrict to known frontend origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup() -> None:
    logger.info("application_starting", service=settings.app_name, env=settings.app_env)


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("application_shutdown", service=settings.app_name)
