from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

datetime.now(UTC)


# =====================================================
# FINANCIAL KPIs
# =====================================================

@dataclass(slots=True)
class FinancialKPIs:

    total_revenue: float
    total_profit: float | None
    profit_margin: float | None
    revenue_growth: float


# =====================================================
# CUSTOMER KPIs
# =====================================================

@dataclass(slots=True)
class CustomerKPIs:

    customer_count: int
    customer_satisfaction: float | None
    customer_churn: float | None
    average_order_value: float


# =====================================================
# PRODUCT KPIs
# =====================================================

@dataclass(slots=True)
class CategoryDistributionItem:

    label: str

    percentage: float


@dataclass(slots=True)
class ProductKPIs:

    top_product: str

    top_category: str

    total_products: int

    category_distribution: list[CategoryDistributionItem]


# =====================================================
# REGION KPIs
# =====================================================

@dataclass(slots=True)
class RegionKPIs:

    top_region: str

    total_regions: int


# =====================================================
# KPI HEALTH
# =====================================================

@dataclass(slots=True)
class KPIHealth:

    business_health: str

    score: float


# =====================================================
# FINAL KPI RESULT
# =====================================================

@dataclass(slots=True)
class KPIResult:

    financial: FinancialKPIs

    customer: CustomerKPIs

    product: ProductKPIs

    region: RegionKPIs

    health: KPIHealth

    generated_at: datetime
    
@dataclass(slots=True)
class KPISection:

    total_revenue: float

    total_profit: float

    revenue_growth: float |None

    profit_margin: float |None

    customer_count: int

    customer_satisfaction: float | None

    customer_churn: float | None

    average_order_value: float

    top_product: str

    top_region: str    