from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_ctx

logger = get_logger("app.exceptions")


class AppException(Exception):
    """Base application exception with standardized code and HTTP status code."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[list[Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class BadRequestError(AppException):
    def __init__(self, message: str = "Invalid request.", code: str = "BAD_REQUEST", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required.", code: str = "UNAUTHORIZED", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden.", code: str = "FORBIDDEN", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_403_FORBIDDEN, details=details)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found.", code: str = "NOT_FOUND", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict.", code: str = "CONFLICT", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_409_CONFLICT, details=details)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed.", code: str = "VALIDATION_ERROR", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Try again later.", code: str = "RATE_LIMIT_EXCEEDED", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_429_TOO_MANY_REQUESTS, details=details)


class InternalServerError(AppException):
    def __init__(self, message: str = "An unexpected error occurred.", code: str = "INTERNAL_SERVER_ERROR", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


class ServiceUnavailableError(AppException):
    def __init__(self, message: str = "Service temporarily unavailable.", code: str = "SERVICE_UNAVAILABLE", details: Optional[list[Any]] = None):
        super().__init__(message=message, code=code, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[list[Any]] = None,
) -> JSONResponse:
    """Build a standardized JSON error response."""
    error_body: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": request_id or request_id_ctx.get(),
    }
    if details:
        error_body["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={"error": error_body},
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        request_id=req_id,
        details=exc.details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI / Pydantic request validation errors."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    formatted_errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error.get("loc", []))
        formatted_errors.append({
            "field": field_path,
            "message": error.get("msg", "Invalid value"),
            "type": error.get("type", "validation_error"),
        })

    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request validation failed. Please check your input parameters.",
        request_id=req_id,
        details=formatted_errors,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette / FastAPI standard HTTP exceptions."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    message = str(exc.detail) if exc.detail else "An HTTP error occurred."

    return build_error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        request_id=req_id,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions to prevent stack trace leaks."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    logger.exception(
        f"Unhandled exception during request {request.method} {request.url.path}: {str(exc)}",
        extra={
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )

    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred. Please contact support.",
        request_id=req_id,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all centralized exception handlers onto the FastAPI application."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
