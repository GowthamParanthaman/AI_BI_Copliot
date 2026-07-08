from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


class DatasetCreate(BaseModel):
    """
    Enterprise Dataset Creation Schema

    Used by:
    - Upload API
    - Ingestion Agent
    - Dataset Service
    - Future ETL Pipelines

    Purpose:
    - Validate incoming dataset metadata
    - Enforce business rules
    - Generate OpenAPI documentation
    """
    
    
    dataset_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Unique business-friendly dataset name",
        examples=["Global Sales Dataset"]
    )

    file_name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Original uploaded file name",
        examples=["sales_2025.csv"]
    )

    file_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Dataset file format",
        examples=["csv"]
    )

    file_size_mb: float = Field(
        default=0.0,
        ge=0,
        description="Dataset size in megabytes"
    )

    row_count: int = Field(
        default=0,
        ge=0,
        description="Total number of rows"
    )

    column_count: int = Field(
        default=0,
        ge=0,
        description="Total number of columns"
    )

    uploaded_by: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User who uploaded dataset"
    )

    department: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Owning department"
    )

    business_domain: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Business domain classification"
    )

    semantic_description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="AI-generated dataset description"
    )

    version: int = Field(
        default=1,
        ge=1,
        description="Dataset version"
    )
    
    file_path: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Physical storage location"
    )

    file_size_mb: float = Field(
        default=0.0,
        ge=0
    )

    row_count: int = Field(
        default=0,
        ge=0
    )

    column_count: int = Field(
        default=0,
        ge=0
    )

    missing_values_count: int = Field(
        default=0,
        ge=0,
        description="Total missing values"
    )

    duplicate_rows_count: int = Field(
        default=0,
        ge=0,
        description="Duplicate row count"
    )

    quality_score: float = Field(
        default=100.0,
        ge=0,
        le=100,
        description="Dataset quality score"
    )

    schema_metadata_json: Optional[str] = Field(
        default=None,
        description="Schema metadata"
    )

    profile_metadata_json: Optional[str] = Field(
        default=None,
        description="Profiling metadata"
    )

    # =====================================================
    # VALIDATORS
    # =====================================================

    @field_validator("dataset_name")
    @classmethod
    def validate_dataset_name(
        cls,
        value: str
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Dataset name cannot be empty"
            )

        return value

    @field_validator("file_type")
    @classmethod
    def validate_file_type(
        cls,
        value: str
    ) -> str:

        allowed_types = {
            "csv",
            "xlsx",
            "xls",
            "parquet",
            "json"
        }

        value = value.lower()

        if value not in allowed_types:

            raise ValueError(
                f"Unsupported file type: {value}"
            )

        return value

    @field_validator("uploaded_by")
    @classmethod
    def validate_uploaded_by(
        cls,
        value: Optional[str]
    ) -> Optional[str]:

        if value:
            value = value.strip()

        return value

    # =====================================================
    # PYDANTIC CONFIG
    # =====================================================

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "dataset_name": "Global Sales Dataset",
                "file_name": "sales_2025.csv",
                "file_type": "csv",
                "file_size_mb": 12.8,
                "row_count": 50000,
                "column_count": 24,
                "uploaded_by": "gowtham",
                "department": "Business Intelligence",
                "business_domain": "Sales",
                "semantic_description": "Enterprise sales transactions dataset",
                "version": 1
            }
        }
    )