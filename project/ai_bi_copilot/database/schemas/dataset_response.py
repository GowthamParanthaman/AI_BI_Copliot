from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class DatasetResponse(BaseModel):
    """
    Enterprise Dataset Response Schema

    Returned by:
    - Dataset API
    - Dashboard APIs
    - Agent APIs
    - Reporting Services

    Purpose:
    - Standardize dataset responses
    - Hide ORM implementation details
    - Provide metadata for BI workflows
    """

    # =====================================================
    # IDENTIFIERS
    # =====================================================

    id: int = Field(
        description="Unique dataset identifier"
    )

    dataset_name: str = Field(
        description="Business-friendly dataset name"
    )

    version: int = Field(
        description="Dataset version"
    )

    # =====================================================
    # FILE INFORMATION
    # =====================================================

    file_name: str = Field(
        description="Original uploaded file"
    )

    file_type: str = Field(
        description="Dataset file format"
    )

    file_size_mb: float = Field(
        description="Dataset size in MB"
    )

    # =====================================================
    # DATASET METRICS
    # =====================================================

    row_count: int = Field(
        description="Total row count"
    )

    column_count: int = Field(
        description="Total column count"
    )

    missing_values_count: int = Field(
        description="Number of missing values"
    )

    duplicate_rows_count: int = Field(
        description="Number of duplicate rows"
    )

    quality_score: float = Field(
        description="Calculated data quality score"
    )

    # =====================================================
    # WORKFLOW STATUS
    # =====================================================

    ingestion_status: str = Field(
        description="Ingestion workflow status"
    )

    cleaning_status: str = Field(
        description="Cleaning workflow status"
    )

    schema_status: str = Field(
        description="Schema validation status"
    )

    analysis_status: str = Field(
        description="Business analysis status"
    )

    # =====================================================
    # BUSINESS METADATA
    # =====================================================

    business_domain: Optional[str] = Field(
        default=None,
        description="Business domain"
    )

    department: Optional[str] = Field(
        default=None,
        description="Owning department"
    )

    uploaded_by: Optional[str] = Field(
        default=None,
        description="Dataset owner"
    )

    semantic_description: Optional[str] = Field(
        default=None,
        description="AI generated dataset summary"
    )

    # =====================================================
    # SYSTEM FLAGS
    # =====================================================

    is_active: bool = Field(
        description="Active flag"
    )

    # =====================================================
    # AUDIT FIELDS
    # =====================================================

    created_at: datetime = Field(
        description="Creation timestamp"
    )

    updated_at: datetime = Field(
        description="Last update timestamp"
    )

    # =====================================================
    # PYDANTIC CONFIG
    # =====================================================

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "id": 1,
                "dataset_name": "Global Sales Dataset",
                "version": 1,
                "file_name": "sales_2025.csv",
                "file_type": "csv",
                "file_size_mb": 12.8,
                "row_count": 50000,
                "column_count": 24,
                "missing_values_count": 125,
                "duplicate_rows_count": 10,
                "quality_score": 96.5,
                "ingestion_status": "COMPLETED",
                "cleaning_status": "COMPLETED",
                "schema_status": "COMPLETED",
                "analysis_status": "PENDING",
                "business_domain": "Sales",
                "department": "Business Intelligence",
                "uploaded_by": "gowtham",
                "semantic_description": "Enterprise sales dataset for KPI analysis",
                "is_active": True,
                "created_at": "2026-06-08T10:00:00",
                "updated_at": "2026-06-08T10:05:00"
            }
        }
    )