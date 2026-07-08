from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from loguru import logger

from schemas.kpi_schema import (
    CustomerKPIs,
    FinancialKPIs,
    KPIHealth,
    KPIResult,
    ProductKPIs,
    RegionKPIs,
)


class KPIService:
    """
    Enterprise KPI Discovery Service.

    Features
    --------
    - Automatic KPI detection
    - Financial KPI calculation
    - Customer KPI calculation
    - Product KPI calculation
    - Region KPI calculation
    - KPI health assessment
    """

    BUSINESS_TERMS = {
        "revenue": [
            "revenue",
            "sales",
            "income",
            "turnover",
            "amount",
            "total amount",
            "total_amount",
            "sales amount",
            "sales_amount",
        ],
        "profit": [
            "profit",
            "net_profit",
            "margin",
            "earnings",
        ],
        "cost": [
            "cost",
            "expense",
        ],
        "customer": [
            "customer",
            "client",
            "buyer",
        ],
        "satisfaction": [
            "satisfaction",
            "rating",
            "score",
            "nps",
        ],
        "churn": [
            "churn",
            "attrition",
            "lost_customer",
            "cancelled",
            "canceled",
        ],
        "product": [
            "product",
            "item",
            "sku",
        ],
        "category": [
            "category",
            "segment",
            "department",
        ],
        "region": [
            "region",
            "country",
            "state",
            "location",
            "territory",
        ],
        "date": [
            "date",
            "order_date",
            "transaction_date",
            "created_at",
            "timestamp",
            "purchase_date",
        ],
    }

    # ==================================================
    # PUBLIC API
    # ==================================================

    def generate_kpis(
        self,
        df: pd.DataFrame,
    ) -> KPIResult:

        logger.info(
            "Generating enterprise KPIs"
        )

        revenue_column = self._find_column(
            df,
            self.BUSINESS_TERMS["revenue"],
        )

        profit_column = self._find_column(
            df,
            self.BUSINESS_TERMS["profit"],
        )

        cost_column = self._find_column(
            df,
            self.BUSINESS_TERMS["cost"],
        )

        financial = self._financial_kpis(
            df=df,
            revenue_column=revenue_column,
            profit_column=profit_column,
            cost_column=cost_column,
        )

        customer = self._customer_kpis(
            df=df,
            revenue_column=revenue_column,
        )

        product = self._product_kpis(
            df
        )

        region = self._region_kpis(
            df
        )

        health = self._kpi_health(
            financial=financial,
            customer=customer,
        )

        result = KPIResult(
            financial=financial,
            customer=customer,
            product=product,
            region=region,
            health=health,
            generated_at=datetime.now(UTC),
        )

        logger.success(
            "KPI generation completed with KPIResult"
        )

        return result

    # ==================================================
    # FINANCIAL KPIS
    # ==================================================

    def _financial_kpis(
        self,
        df: pd.DataFrame,
        revenue_column: str | None,
        profit_column: str | None,
        cost_column: str | None,
    ) -> FinancialKPIs:

        total_revenue = (
            self._safe_sum(df[revenue_column])
            if revenue_column
            else 0.0
        )

        total_profit = self._calculate_total_profit(
            df=df,
            revenue_column=revenue_column,
            profit_column=profit_column,
            cost_column=cost_column,
        )

        profit_margin = (
            round(
                (total_profit / total_revenue) * 100,
                2,
            )
            if (
                total_profit is not None
                and total_revenue > 0
            )
            else None
        )

        revenue_growth = self._calculate_revenue_growth(
            df=df,
            revenue_column=revenue_column,
        )

        logger.info(
            "Financial KPIs calculated | "
            f"revenue={total_revenue} | "
            f"profit={total_profit} | "
            f"margin={profit_margin} | "
            f"growth={revenue_growth}"
        )

        return FinancialKPIs(
            total_revenue=total_revenue,
            total_profit=total_profit,
            profit_margin=profit_margin,
            revenue_growth=revenue_growth,
        )

    def _calculate_total_profit(
        self,
        df: pd.DataFrame,
        revenue_column: str | None,
        profit_column: str | None,
        cost_column: str | None,
    ) -> float | None:

        if profit_column:
            return self._safe_sum(
                df[profit_column]
            )

        if revenue_column and cost_column:
            return round(
                self._safe_sum(df[revenue_column])
                - self._safe_sum(df[cost_column]),
                2,
            )

        logger.warning(
            "Unable to calculate total profit."
        )

        return None

    def _calculate_revenue_growth(
        self,
        df: pd.DataFrame,
        revenue_column: str | None,
    ) -> float:

        if not revenue_column:
            return 0.0

        revenue_series = pd.to_numeric(
            df[revenue_column],
            errors="coerce",
        ).fillna(0)

        if len(revenue_series) < 2:
            return 0.0

        date_column = self._find_column(
            df,
            self.BUSINESS_TERMS["date"],
        )

        if date_column:
            dated_frame = df[[date_column, revenue_column]].copy()

            dated_frame[date_column] = pd.to_datetime(
                dated_frame[date_column],
                errors="coerce",
            )

            dated_frame[revenue_column] = pd.to_numeric(
                dated_frame[revenue_column],
                errors="coerce",
            ).fillna(0)

            dated_frame = dated_frame.dropna(
                subset=[date_column]
            ).sort_values(
                by=date_column
            )

            if len(dated_frame) >= 2:
                revenue_series = dated_frame[revenue_column]

        midpoint = len(revenue_series) // 2

        if midpoint == 0:
            return 0.0

        previous_revenue = float(
            revenue_series.iloc[:midpoint].sum()
        )

        current_revenue = float(
            revenue_series.iloc[midpoint:].sum()
        )

        if previous_revenue == 0:
            return 0.0

        return round(
            (
                (current_revenue - previous_revenue)
                / abs(previous_revenue)
            )
            * 100,
            2,
        )

    # ==================================================
    # CUSTOMER KPIS
    # ==================================================

    def _customer_kpis(
        self,
        df: pd.DataFrame,
        revenue_column: str | None,
    ) -> CustomerKPIs:

        customer_column = self._find_column(
            df,
            self.BUSINESS_TERMS["customer"],
        )

        satisfaction_column = self._find_column(
            df,
            self.BUSINESS_TERMS["satisfaction"],
        )

        churn_column = self._find_column(
            df,
            self.BUSINESS_TERMS["churn"],
        )

        customer_count = (
            int(df[customer_column].nunique())
            if customer_column
            else int(len(df))
        )

        customer_satisfaction = (
            self._safe_mean(df[satisfaction_column])
            if satisfaction_column
            else None
        )

        customer_churn = (
            self._safe_mean(df[churn_column])
            if churn_column
            else None
        )

        

        average_order_value = (
            self._safe_mean(df[revenue_column])
            if revenue_column
            else 0.0
        )

        logger.info(
            "Customer KPIs calculated | "
            f"count={customer_count} | "
            f"satisfaction={customer_satisfaction} | "
            f"churn={customer_churn} | "
            f"aov={average_order_value}"
        )

        return CustomerKPIs(
            customer_count=customer_count,
            customer_satisfaction=customer_satisfaction,
            customer_churn=customer_churn,
            average_order_value=average_order_value,
        )

    # ==================================================
    # PRODUCT KPIS
    # ==================================================

    def _product_kpis(
        self,
        df: pd.DataFrame,
    ) -> ProductKPIs:

        product_column = self._find_column(
            df,
            self.BUSINESS_TERMS["product"],
        )

        category_column = self._find_column(
            df,
            self.BUSINESS_TERMS["category"],
        )

        top_product = self._top_value(
            df=df,
            column=product_column,
            fallback="Unknown",
        )

        top_category = self._top_value(
            df=df,
            column=category_column,
            fallback="Unknown",
        )

        total_products = (
            int(df[product_column].nunique())
            if product_column
            else 0
        )

        logger.info(
            "Product KPIs calculated | "
            f"top_product={top_product} | "
            f"top_category={top_category} | "
            f"total_products={total_products}"
        )

        return ProductKPIs(
            top_product=top_product,
            top_category=top_category,
            total_products=total_products,
        )

    # ==================================================
    # REGION KPIS
    # ==================================================

    def _region_kpis(
        self,
        df: pd.DataFrame,
    ) -> RegionKPIs:

        region_column = self._find_column(
            df,
            self.BUSINESS_TERMS["region"],
        )

        top_region = self._top_value(
            df=df,
            column=region_column,
            fallback="Unknown",
        )

        total_regions = (
            int(df[region_column].nunique())
            if region_column
            else 0
        )

        logger.info(
            "Region KPIs calculated | "
            f"top_region={top_region} | "
            f"total_regions={total_regions}"
        )

        return RegionKPIs(
            top_region=top_region,
            total_regions=total_regions,
        )

    # ==================================================
    # KPI HEALTH
    # ==================================================

    def _kpi_health(
        self,
        financial: FinancialKPIs,
        customer: CustomerKPIs,
    ) -> KPIHealth:

        score = 0.0

        if financial.revenue_growth >= 20:
            score += 25
        elif financial.revenue_growth >= 10:
            score += 20
        elif financial.revenue_growth >= 0:
            score += 15
        else:
            score += 5

        profit_margin = financial.profit_margin or 0.0

        if profit_margin >= 25:
            score += 25
        elif profit_margin >= 15:
            score += 20
        elif profit_margin >= 10:
            score += 15
        else:
            score += 5

        customer_satisfaction = (
            customer.customer_satisfaction or 0.0
        )

        if customer_satisfaction >= 90:
            score += 25
        elif customer_satisfaction >= 75:
            score += 20
        elif customer_satisfaction > 0:
            score += 15
        else:
            score += 10

        customer_churn = (
            customer.customer_churn or 0.0
        )

        if customer_churn <= 5:
            score += 25
        elif customer_churn <= 10:
            score += 20
        elif customer_churn <= 20:
            score += 15
        else:
            score += 5

        if score >= 90:
            business_health = "EXCELLENT"
        elif score >= 75:
            business_health = "GOOD"
        elif score >= 50:
            business_health = "FAIR"
        else:
            business_health = "CRITICAL"

        logger.info(
            "KPI health calculated | "
            f"score={score} | "
            f"business_health={business_health}"
        )

        return KPIHealth(
            business_health=business_health,
            score=round(score, 2),
        )

    # ==================================================
    # COLUMN DETECTION
    # ==================================================

    def _find_column(
        self,
        df: pd.DataFrame,
        keywords: list[str],
    ) -> str | None:

        logger.info(
            f"Searching columns: {list(df.columns)}"
        )

        for column in df.columns:

            column_name = (
                str(column)
                .lower()
                .strip()
            )

            if any(
                keyword in column_name
                for keyword in keywords
            ):

                logger.info(
                    f"Matched column: {column}"
                )

                return str(column)

        logger.warning(
            f"No match found for keywords: {keywords}"
        )

        return None

    @staticmethod
    def _top_value(
        df: pd.DataFrame,
        column: str | None,
        fallback: str,
    ) -> str:

        if not column:
            return fallback

        values = df[column].dropna()

        if values.empty:
            return fallback

        return str(
            values.value_counts().idxmax()
        )

    # ==================================================
    # SAFE NUMERIC HELPERS
    # ==================================================

    @staticmethod
    def _safe_sum(
        series: pd.Series,
    ) -> float:

        return round(
            float(
                pd.to_numeric(
                    series,
                    errors="coerce",
                )
                .fillna(0)
                .sum()
            ),
            2,
        )

    @staticmethod
    def _safe_mean(
        series: pd.Series,
    ) -> float:

        return round(
            float(
                pd.to_numeric(
                    series,
                    errors="coerce",
                )
                .fillna(0)
                .mean()
            ),
            2,
        )