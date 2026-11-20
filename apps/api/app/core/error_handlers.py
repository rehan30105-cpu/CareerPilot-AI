"""Centralized error handling for the FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger

logger = get_logger("error_handlers")


def register_error_handlers(app: FastAPI) -> None:
    """Register exception handlers that return consistent JSON error responses."""

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error(
            "database_error",
            path=request.url.path,
            method=request.method,
            error=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "database_error",
                "message": "A database error occurred.",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "unhandled_error",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred.",
            },
        )
