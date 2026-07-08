from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from schemas.kpi_schema import KPIResult


@dataclass(slots=True)
class BusinessAnalysisResult:
    """
    Structured output produced by BusinessAnalysisAgent.
    """

    business_health: str

    executive_summary: str

    recommendations: list[str]

    risks: list[str]

    opportunities: list[str]

    kpis: KPIResult

    generated_at: datetime