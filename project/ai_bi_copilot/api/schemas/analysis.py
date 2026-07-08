from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AnalysisRequest(BaseModel):
    """
    Analysis Workflow Request

    Used by:
    - FastAPI
    - Streamlit
    - External Clients
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    dataset_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique dataset identifier",
        examples=["sales_2025"]
    )

    question: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional business question"
    )


class AnalysisResponse(BaseModel):
    """
    Analysis Workflow Response
    """

    model_config = ConfigDict(
        extra="ignore"
    )
    
    chart_paths: list[str] | None = None

    chart_metadata: list[dict[str, Any]] | None = None

    # ==========================================
    # EXECUTION
    # ==========================================

    success: bool

    execution_id: str | None = None

    execution_status: str | None = None

    execution_time_seconds: float | None = None

    generated_at: datetime

    error: str | None = None

    # ==========================================
    # DATASET
    # ==========================================

    dataset_name: str

    # ==========================================
    # PIPELINE OUTPUT
    # ==========================================

    kpis: dict[str, Any] | None = None

    forecast_results: dict[str, Any] | None = None

    anomalies: list[dict[str, Any]] | None = None

    root_causes: dict[str, Any] | None = None

    health_score: dict[str, Any] | None = None

    alerts: dict[str, Any] | None = None

    insights: dict[str, Any] | None = None

    recommendations: dict[str, Any] | None = None

    action_plan: dict[str, Any] | None = None

    business_analysis: dict[str, Any] | None = None

    dashboard: dict[str, Any] | None = None

    report: str | None = None

    visualizations: list[dict[str, Any]] | None = None

    agent_metrics: dict[str, Any] | None = None

    agent_errors: list[dict[str, Any]] | None = None
    
    report_pdf_path: str | None = None