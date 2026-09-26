# Ashtalakshmi MRV Platform

## Overview
The Ashtalakshmi Measurement, Reporting, and Verification (MRV) platform is a comprehensive system designed for forest monitoring and carbon assessment. It provides tools for processing satellite data, analyzing biomass using machine learning models, and serving spatial data and reports.

## Architecture
- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + GeoAlchemy2 + Pydantic v2
- **Database:** PostgreSQL 16 + PostGIS 3.4
- **Task Queue:** Celery 5.4 + Redis 7.2
- **Object Storage:** MinIO (S3-compatible)
- **Tiling Services:** TiTiler (raster) and pg_tileserv (vector)
- **Machine Learning:** LightGBM for biomass estimation

## Quick Start

1. **Start the Infrastructure:**
   Ensure you have Docker and Docker Compose installed.
   ```bash
   docker-compose up -d
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Configure Environment:**
   Copy `.env.example` to `.env` and update the necessary credentials.

4. **Run the Application:**
   ```bash
   uvicorn backend.api.main:app --reload
   ```

## API Documentation
Once the application is running, the interactive API documentation will be available at:
[http://localhost:8000/docs](http://localhost:8000/docs)
