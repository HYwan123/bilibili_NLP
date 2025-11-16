from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    def __init__(self, message: str = "Database connection failed"):
        self.message = message
        super().__init__(self.message)

class RedisConnectionError(Exception):
    """Raised when Redis connection fails"""
    def __init__(self, message: str = "Redis connection failed"):
        self.message = message
        super().__init__(self.message)

class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIError):
    """Raised when validation fails"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 422)

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

def log_error(error: Exception, context: str = ""):
    """Log error with context and traceback"""
    error_msg = f"{context} - {str(error)} - Traceback: {traceback.format_exc()}"
    logger.error(error_msg)

def create_error_response(status_code: int, message: str, details: Any = None) -> JSONResponse:
    """Create a standardized error response"""
    error_data = {
        "code": status_code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "success": False
    }

    if details:
        error_data["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors"""
    log_error(exc, f"Validation error in {request.url}")
    return create_error_response(
        exc.status_code,
        exc.message,
        {"path": str(request.url), "method": request.method}
    )

async def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle not found errors"""
    log_error(exc, f"Not found error in {request.url}")
    return create_error_response(
        exc.status_code,
        exc.message,
        {"path": str(request.url), "method": request.method}
    )

async def handle_database_error(request: Request, exc: DatabaseConnectionError) -> JSONResponse:
    """Handle database connection errors"""
    log_error(exc, f"Database error in {request.url}")
    return create_error_response(
        500,
        "Database connection failed",
        {"path": str(request.url), "method": request.method}
    )

async def handle_general_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle general errors"""
    log_error(exc, f"General error in {request.url}")
    return create_error_response(
        500,
        "Internal server error occurred",
        {"path": str(request.url), "method": request.method}
    )

def register_exception_handlers(app):
    """Register exception handlers with the FastAPI app"""
    app.add_exception_handler(ValidationError, handle_validation_error)
    app.add_exception_handler(NotFoundError, handle_not_found_error)
    app.add_exception_handler(DatabaseConnectionError, handle_database_error)
    app.add_exception_handler(Exception, handle_general_error)