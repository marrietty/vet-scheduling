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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import BACKEND_CORS_ORIGINS, LOG_LEVEL
from app.core.database import init_db
from app.features.auth.router import router as auth_router
from app.features.pets.router import router as pets_router
from app.features.appointments.router import router as appointments_router
from app.features.clinic.router import router as clinic_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database tables
    - Shutdown: Cleanup (if needed)
    
    Requirements: 12.8
    """
    # Startup: Create database tables
    logger.info("Starting Vet Clinic Scheduling System API...")
    logger.info("Initializing database tables...")
    try:
        init_db()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Cleanup (if needed in the future)
    logger.info("Application shutting down...")


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


# Include all feature routers
app.include_router(auth_router)
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
