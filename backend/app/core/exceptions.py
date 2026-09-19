"""Custom exception classes and FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=msg, status_code=404)


class UnauthorizedError(AppException):
    """Authentication required or failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class ForbiddenError(AppException):
    """Permission denied."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message=message, status_code=403)


class ConflictError(AppException):
    """Resource already exists or conflicts."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


class ValidationError(AppException):
    """Input validation failed."""

    def __init__(self, message: str = "Validation failed", details: dict | None = None):
        super().__init__(message=message, status_code=422, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log the real error server-side, return friendly message to client
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An unexpected error occurred. Please try again later.",
                "details": {},
            },
        )
