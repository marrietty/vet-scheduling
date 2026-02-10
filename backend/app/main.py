"""
Main FastAPI application entry point.

This module initializes the FastAPI application with:
- All feature routers (auth, pets, appointments, clinic)
- CORS middleware configuration
- Database table creation on startup
- API documentation at /docs
- Logging configuration

Requirements: 11.1, 12.8
"""

import logging
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import BACKEND_CORS_ORIGINS, LOG_LEVEL
from app.core.database import init_db
from app.features.auth.router import router as auth_router
from app.features.users.router import router as users_router
from app.features.pets.router import router as pets_router
from app.features.appointments.router import router as appointments_router
from app.features.clinic.router import router as clinic_router
from app.features.auth.tasks import cleanup_expired_tokens
from app.common.exceptions import (
    TokenBlacklistedException,
    ProfileUpdateForbiddenException,
    AppointmentRescheduleForbiddenException,
    TimeSlotUnavailableException
)
from app.common.error_responses import ErrorResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Background task control
cleanup_task = None


async def periodic_token_cleanup(interval_hours: int = 24):
    """
    Periodically run token cleanup task.
    
    This background task runs in a loop, cleaning up expired tokens from the
    blacklist at the specified interval. It runs continuously until the
    application shuts down.
    
    Args:
        interval_hours: Hours between cleanup runs (default: 24 hours)
        
    Requirements:
        - 7.3: Provide mechanism to periodically remove expired tokens
    """
    logger.info(f"Token cleanup task started. Will run every {interval_hours} hours.")
    
    while True:
        try:
            # Wait for the specified interval
            await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
            
            # Run the cleanup
            logger.info("Running scheduled token cleanup...")
            count = cleanup_expired_tokens()
            logger.info(f"Scheduled cleanup completed: removed {count} expired token(s)")
            
        except asyncio.CancelledError:
            logger.info("Token cleanup task cancelled, shutting down...")
            break
        except Exception as e:
            logger.error(f"Error in periodic token cleanup: {str(e)}", exc_info=True)
            # Continue running even if one cleanup fails
            continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database tables and start background tasks
    - Shutdown: Cancel background tasks and cleanup
    
    Requirements: 12.8, 7.3
    """
    global cleanup_task
    
    # Startup: Create database tables
    logger.info("Starting Vet Clinic Scheduling System API...")
    logger.info("Initializing database tables...")
    try:
        init_db()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Start background task for token cleanup
    logger.info("Starting background task for token cleanup...")
    cleanup_task = asyncio.create_task(periodic_token_cleanup(interval_hours=24))
    
    yield
    
    # Shutdown: Cancel background tasks
    logger.info("Application shutting down...")
    if cleanup_task:
        logger.info("Cancelling token cleanup task...")
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            logger.info("Token cleanup task cancelled successfully")
    logger.info("Shutdown complete.")


# Initialize FastAPI application
app = FastAPI(
    title="Vet Clinic Scheduling System API",
    description="REST API backend for a veterinary clinic scheduling system with role-based access control",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {BACKEND_CORS_ORIGINS}")


# Register exception handlers
@app.exception_handler(TokenBlacklistedException)
async def token_blacklisted_exception_handler(request: Request, exc: TokenBlacklistedException):
    """
    Handle TokenBlacklistedException with consistent error response format.
    
    Returns HTTP 401 with error details including timestamp and error type.
    
    Requirements: 1.2
    """
    error_response = ErrorResponse.create(
        detail=exc.detail,
        error_type="token_blacklisted"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=exc.headers
    )


@app.exception_handler(ProfileUpdateForbiddenException)
async def profile_update_forbidden_exception_handler(request: Request, exc: ProfileUpdateForbiddenException):
    """
    Handle ProfileUpdateForbiddenException with consistent error response format.
    
    Returns HTTP 403 with error details including timestamp and error type.
    
    Requirements: 3.7
    """
    error_response = ErrorResponse.create(
        detail=exc.detail,
        error_type="profile_update_forbidden"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(AppointmentRescheduleForbiddenException)
async def appointment_reschedule_forbidden_exception_handler(request: Request, exc: AppointmentRescheduleForbiddenException):
    """
    Handle AppointmentRescheduleForbiddenException with consistent error response format.
    
    Returns HTTP 403 with error details including timestamp and error type.
    
    Requirements: 6.6
    """
    error_response = ErrorResponse.create(
        detail=exc.detail,
        error_type="appointment_reschedule_forbidden"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(TimeSlotUnavailableException)
async def time_slot_unavailable_exception_handler(request: Request, exc: TimeSlotUnavailableException):
    """
    Handle TimeSlotUnavailableException with consistent error response format.
    
    Returns HTTP 409 with error details including timestamp and error type.
    
    Requirements: 6.9
    """
    error_response = ErrorResponse.create(
        detail=exc.detail,
        error_type="time_slot_unavailable"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


# Include all feature routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(pets_router)
app.include_router(appointments_router)
app.include_router(clinic_router)

logger.info("All routers registered successfully")


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint providing API information.
    
    Returns:
        API welcome message and documentation links
    """
    return {
        "message": "Welcome to Vet Clinic Scheduling System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        API health status
    """
    return {"status": "healthy"}
