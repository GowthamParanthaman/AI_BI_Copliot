from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


# ======================================================
# REPORT HEADER
# ======================================================

@dataclass(slots=True)
class ReportHeader:

    title: str

    company_name: str

    dataset_name: str

    generated_at: datetime


@dataclass(slots=True)
class KPISection:

    total_revenue: float

    total_profit: float

    revenue_growth: float

    profit_margin: float

    customer_count: int

    customer_satisfaction: float

    customer_churn: float

    average_order_value: float

    top_product: str

    top_region: str


# ======================================================
# BUSINESS SECTION
# ======================================================

@dataclass(slots=True)
class BusinessSection:

    health: str

    executive_summary: str

    key_findings: list[str]

    risks: list[str]

    opportunities: list[str]

    recommendations: list[str]


# ======================================================
# TREND SECTION
# ======================================================

@dataclass(slots=True)
class TrendSection:

    trends: list[str]


# ======================================================
# RISK SECTION
# ======================================================

@dataclass(slots=True)
class RiskSection:

    critical: list[str]

    medium: list[str]

    low: list[str]


# ======================================================
# OPPORTUNITY SECTION
# ======================================================

@dataclass(slots=True)
class OpportunitySection:

    opportunities: list[str]


# ======================================================
# RECOMMENDATION SECTION
# ======================================================

@dataclass(slots=True)
class RecommendationSection:

    strategic: list[str]

    operational: list[str]

    automation: list[str]


# ======================================================
# VISUALIZATION SECTION
# ======================================================

@dataclass(slots=True)
class VisualizationSection:

    charts: list[dict[str, Any]]


# ======================================================
# REPORT FOOTER
# ======================================================

@dataclass(slots=True)
class ReportFooter:

    generated_by: str

    model: str

    version: str

    generated_at: datetime


# ======================================================
# EXECUTIVE REPORT
# ======================================================

@dataclass(slots=True)
class ExecutiveReport:

    header: ReportHeader

    executive_summary: str

    kpis: KPISection

    business: BusinessSection

    trends: TrendSection

    risks: RiskSection

    opportunities: OpportunitySection

    recommendations: RecommendationSection

    visualizations: VisualizationSection

    executive_decision: str

    footer: ReportFooter

    generated_at: datetime