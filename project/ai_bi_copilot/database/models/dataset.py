from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base


class Dataset(Base):
    """
    Enterprise Dataset Entity

    Represents a business dataset managed by
    the AI Business Intelligence Copilot.

    Capabilities
    ------------
    - File lineage tracking
    - Dataset profiling
    - KPI generation metadata
    - AI analysis metadata
    - Workflow monitoring
    - Audit history
    """

    __tablename__ = "datasets"

    __table_args__ = (

        Index(
            "idx_dataset_name",
            "dataset_name"
        ),

        Index(
            "idx_pipeline_status",
            "pipeline_status"
        ),

        Index(
            "idx_created_at",
            "created_at"
        ),

        Index(
            "idx_business_domain",
            "business_domain"
        ),
    )

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ==================================================
    # DATASET INFORMATION
    # ==================================================

    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    file_size_mb: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    # ==================================================
    # STORAGE METADATA
    # ==================================================

    file_path: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )

    file_hash: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        unique=True
    )

    # ==================================================
    # DATA QUALITY
    # ==================================================

    row_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    column_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    missing_values_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    duplicate_rows_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    quality_score: Mapped[float] = mapped_column(
        Float,
        default=100.0
    )

    # ==================================================
    # DATA PROFILING
    # ==================================================

    schema_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    profile_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # ==================================================
    # AI METADATA
    # ==================================================

    semantic_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    business_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    recommended_kpis_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    anomaly_summary_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    forecast_summary_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # ==================================================
    # BUSINESS OWNERSHIP
    # ==================================================

    uploaded_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    business_domain: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    # ==================================================
    # PIPELINE STATUS
    # ==================================================

    ingestion_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING"
    )

    cleaning_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING"
    )

    schema_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING"
    )

    analysis_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING"
    )

    pipeline_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING"
    )

    # ==================================================
    # EXECUTION METRICS
    # ==================================================

    analysis_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    last_analyzed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    last_execution_time_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    # ==================================================
    # VERSIONING
    # ==================================================

    version: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    # ==================================================
    # AUDIT
    # ==================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ==================================================
    # COMPUTED PROPERTIES
    # ==================================================

    @property
    def is_profiled(self) -> bool:
        return self.profile_json is not None

    @property
    def is_analyzed(self) -> bool:
        return self.analysis_status == "COMPLETED"

    @property
    def is_high_quality(self) -> bool:
        return self.quality_score >= 85

    @property
    def dataset_size_label(self) -> str:

        if self.row_count < 10_000:
            return "SMALL"

        if self.row_count < 1_000_000:
            return "MEDIUM"

        return "LARGE"