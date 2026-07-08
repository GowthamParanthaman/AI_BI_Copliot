"""
Database Schema Package

Purpose:
    Centralized exports for all Pydantic schemas.

Used By:
    - FastAPI Routes
    - Service Layer
    - Agent Layer
    - API Documentation
    - Validation Layer

Example:
    from database.schemas import (
        DatasetCreate,
        DatasetResponse
    )
"""

from database.schemas.dataset_create import (
    DatasetCreate,
)

from database.schemas.dataset_response import (
    DatasetResponse,
)

__all__ = [
    "DatasetCreate",
    "DatasetResponse",
]

__version__ = "1.0.0"