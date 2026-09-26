"""
Ashtalakshmi MRV Platform - FastAPI Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.api.auth import router as auth_router
from backend.api.projects import router as projects_router
from backend.api.field_data import router as field_data_router
from backend.api.satellite import router as satellite_router
from backend.api.carbon import router as carbon_router
from backend.api.audit import router as audit_router
from backend.schemas.common import HealthResponse
from backend.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("🌲 Starting Ashtalakshmi MRV Platform")
    logger.info(f"   Database: {'SQLite (local dev)' if settings.is_sqlite else 'PostgreSQL+PostGIS'}")

    # Auto-create tables for SQLite local dev mode
    if settings.is_sqlite:
        from backend.database import create_all_tables
        await create_all_tables()
        logger.info("   ✅ SQLite database tables created")

    logger.info("   ✅ Platform ready at http://localhost:8000")
    logger.info("   📚 API docs at http://localhost:8000/docs")
    yield
    logger.info("🛑 Shutting down Ashtalakshmi MRV Platform")


app = FastAPI(
    title="Ashtalakshmi MRV Platform",
    description=(
        "Measurement, Reporting, and Verification platform for forest/plantation "
        "monitoring and carbon assessment. Built for the NESFIC-D-15 challenge "
        "under the Ashtalakshmi initiative (Assam)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(field_data_router)
app.include_router(satellite_router)
app.include_router(carbon_router)
app.include_router(audit_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - platform welcome."""
    return {
        "name": "Ashtalakshmi MRV Platform",
        "version": "1.0.0",
        "description": "Forest monitoring and carbon assessment for Assam",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="OK",
        database="SQLite" if settings.is_sqlite else "PostgreSQL",
        redis="Not configured (local dev)" if settings.is_sqlite else "OK",
        minio="Not configured (local dev)" if settings.is_sqlite else "OK",
    )
