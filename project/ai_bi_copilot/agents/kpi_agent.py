from __future__ import annotations

from datetime import datetime,UTC
from typing import Any

import pandas as pd
from dataclasses import asdict
from loguru import logger
from schemas.kpi_schema import (
    KPIResult,
    FinancialKPIs,
    CustomerKPIs,
    ProductKPIs,
    RegionKPIs,
    KPIHealth,
)

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState

class KPIAgent(BaseAgent):
    """
    Enterprise KPI Intelligence Agent

    ```
    Responsibilities
    ----------------
    - KPI Discovery
    - KPI Classification
    - KPI Calculation
    - KPI Health Assessment
    - Executive KPI Summary
    - LLM Context Generation
    """

    agent_name = "KPIAgent"
    agent_version = "2.0.0"

    KPI_PATTERNS = {

        "revenue": [
            "revenue",
            "sales",
            "income",
            "turnover",
            "amount",
            "total amount",
            "sales amount",
            "total_amount"
        ],

        "profit": [
            "profit",
            "margin",
            "earnings"
        ],

        "cost": [
            "cost",
            "expense"
        ],

        "customer": [
            "customer",
            "client",
            "buyer"
        ],

        "quantity": [
            "quantity",
            "qty",
            "units"
        ]
    }

    # ==================================================
    # EXECUTION
    # ==================================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting KPI analysis"
        )

        logger.warning(
            "CUSTOM KPI AGENT LOADED"
        )

        self.validate_input(state)

        df = state.get("dataframe")

        if df is None:
            raise ValueError(
                "dataframe missing from workflow state"
            )

        logger.info(
            f"KPI Columns = {list(df.columns)}"
        )

        # ==================================================
        # RAW KPI CALCULATIONS
        # ==================================================

        financial = self._financial_kpis(df)

        product = self._product_kpis(df)

        category = self._category_kpis(df)

        region = self._region_kpis(df)

        # ==================================================
        # BUILD KPI SCHEMA
        # ==================================================

        financial_result = FinancialKPIs(

            total_revenue=financial.get(
                "total_revenue",
                0.0
            ),

            total_profit=financial.get(
                "total_profit",
                0.0
            ),

            profit_margin=financial.get(
                "profit_margin",
                0.0
            ),

            revenue_growth=financial.get(
                "revenue_growth",
                0.0
            ),
        )

        customer_result = CustomerKPIs(

            customer_count=financial.get(
                "total_orders",
                0
            ),

            customer_satisfaction=financial.get(
                "customer_satisfaction",
                0.0
            ),

            customer_churn=financial.get(
                "customer_churn",
                0.0
            ),

            average_order_value=financial.get(
                "average_order_value",
                0.0
            ),
        )

        product_result = ProductKPIs(

            top_product=product.get(
                "top_product",
                "Unknown"
            ),

            top_category=category.get(
                "top_category",
                "Unknown"
            ),

            total_products=product.get(
                "total_products",
                0
            ),
        )

        region_result = RegionKPIs(

            top_region=region.get(
                "top_region",
                "Unknown"
            ),

            total_regions=region.get(
                "total_regions",
                0
            ),
        )

        # ==================================================
        # HEALTH SCORE
        # ==================================================

        score = 85

        if financial_result.revenue_growth >= 20:
            score += 5

        if financial_result.profit_margin >= 20:
            score += 5

        if score >= 90:
            health = "EXCELLENT"
        elif score >= 75:
            health = "GOOD"
        elif score >= 50:
            health = "FAIR"
        else:
            health = "CRITICAL"

        health_result = KPIHealth(

            business_health=health,

            score=score,
        )

        # ==================================================
        # FINAL KPI RESULT
        # ==================================================

        kpi_result = KPIResult(

            financial=financial_result,

            customer=customer_result,

            product=product_result,

            region=region_result,

            health=health_result,

            generated_at=datetime.now(UTC),
        )

        # ==================================================
        # LEGACY KPI SUPPORT
        # ==================================================

        discovered_kpis = self._discover_kpis(df)

        kpi_metrics = self._calculate_kpis(
            df=df,
            discovered_kpis=discovered_kpis,
        )

        kpi_health = self._evaluate_kpi_health(
            kpi_metrics
        )

        executive_summary = self._generate_executive_summary(
            kpi_metrics
        )

        llm_context = self._generate_llm_context(
            kpi_metrics
        )

        # ==================================================
        # STATE UPDATE
        # ==================================================

        # New dataclass
        state["kpi_result"] = kpi_result

        # Legacy dictionary (temporary compatibility)
        state["kpis"] = asdict(kpi_result)

        state["kpi_status"] = "COMPLETED"

        state["kpi_generated_at"] = datetime.now(
            UTC
        ).isoformat()

        state["discovered_kpis"] = discovered_kpis

        state["kpi_metrics"] = kpi_metrics

        state["kpi_health"] = kpi_health

        state["executive_kpi_summary"] = executive_summary

        state["kpi_llm_context"] = llm_context

        state["kpi_generated_at"] = datetime.now(
            UTC
        ).isoformat()

        state["discovered_kpis"] = discovered_kpis

        state["kpi_metrics"] = kpi_metrics

        state["kpi_health"] = kpi_health

        state["executive_kpi_summary"] = executive_summary

        state["kpi_llm_context"] = llm_context

        self.validate_output(state)

        logger.success(
            f"[{self.agent_name}] KPI generation completed"
        )

        return state
    # ==================================================
    # VALIDATION
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        if "dataframe" not in state:

            raise ValueError(
                "dataframe missing from workflow state"
            )

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        required = [

            "kpi_status",

            "kpi_result",

            "kpis",
        ]

        missing = [

            field
            for field in required
            if field not in state
        ]

        if missing:

            raise RuntimeError(
                f"Missing KPI outputs: {missing}"
            )

    # ==================================================
    # KPI DISCOVERY
    # ==================================================

    def _discover_kpis(
        self,
        df: pd.DataFrame
    ) -> dict[str, list[str]]:

        result = {}

        for category, keywords in (
            self.KPI_PATTERNS.items()
        ):

            matched_columns = []

            for column in df.columns:

                column_name = (
                    column.lower()
                )

                if any(
                    keyword in column_name
                    for keyword in keywords
                ):

                    matched_columns.append(
                        column
                    )

            result[category] = (
                matched_columns
            )

        return result

    # ==================================================
    # KPI CALCULATIONS
    # ==================================================

    def _calculate_kpis(
        self,
        df: pd.DataFrame,
        discovered_kpis: dict[str, list[str]]
    ) -> dict[str, Any]:

        results = {}

        for category, columns in (
            discovered_kpis.items()
        ):

            category_result = {}

            for column in columns:

                if (
                    column not in df.columns
                    or not pd.api.types.is_numeric_dtype(
                        df[column]
                    )
                ):
                    continue

                category_result[column] = {

                    "sum":
                        round(
                            float(
                                df[column].sum()
                            ),
                            2
                        ),

                    "average":
                        round(
                            float(
                                df[column].mean()
                            ),
                            2
                        ),

                    "minimum":
                        round(
                            float(
                                df[column].min()
                            ),
                            2
                        ),

                    "maximum":
                        round(
                            float(
                                df[column].max()
                            ),
                            2
                        ),

                    "median":
                        round(
                            float(
                                df[column].median()
                            ),
                            2
                        )
                }

            results[category] = (
                category_result
            )

        return results

    # ==================================================
    # KPI HEALTH
    # ==================================================

    def _evaluate_kpi_health(
        self,
        metrics: dict[str, Any]
    ) -> dict[str, str]:

        health = {}

        for category, values in (
            metrics.items()
        ):

            if not values:

                health[category] = (
                    "UNKNOWN"
                )

                continue

            health[category] = (
                "HEALTHY"
            )

        return health

    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================

    def _generate_executive_summary(
        self,
        metrics: dict[str, Any]
    ) -> list[str]:

        summary = []

        for category, values in (
            metrics.items()
        ):

            if not values:
                continue

            summary.append(
                f"{category.title()} "
                f"contains "
                f"{len(values)} KPI metrics."
            )

        return summary

    # ==================================================
    # LLM CONTEXT
    # ==================================================

    def _generate_llm_context(
        self,
        metrics: dict[str, Any]
    ) -> str:

        context = []

        for category, values in (
            metrics.items()
        ):

            if not values:
                continue

            context.append(
                f"{category.upper()} KPIs:"
            )

            for metric_name, metric_values in (
                values.items()
            ):

                context.append(
                    f"{metric_name}: "
                    f"Sum={metric_values['sum']}, "
                    f"Avg={metric_values['average']}"
                )

        return "\n".join(context)

    def _financial_kpis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        logger.warning(
            f"KPI INPUT COLUMNS: {list(df.columns)}"
        )

        financial = {}

        revenue_column = None

        revenue_keywords = [

            "revenue",
            "sales",
            "amount",
            "total_amount",
            "sales_amount",
            "gross_sales",
            "net_sales",
            "income"
        ]

        for col in df.columns:

            column = str(col).lower().strip()

            if any(
                keyword in column
                for keyword in revenue_keywords
            ):

                revenue_column = col

                logger.success(
                    f"Revenue column found: {col}"
                )

                break

        logger.warning(
            f"Final revenue column: {revenue_column}"
        )

        if revenue_column:

            financial["total_revenue"] = round(
                float(df[revenue_column].sum()),
                2
            )

            financial["average_order_value"] = round(
                float(df[revenue_column].mean()),
                2
            )

            financial["max_order_value"] = round(
                float(df[revenue_column].max()),
                2
            )

            financial["min_order_value"] = round(
                float(df[revenue_column].min()),
                2
            )

            financial["total_orders"] = int(
                len(df)
            )

        logger.warning(
            f"Financial KPIs GENERATED: {financial}"
        )

        return financial

        # ==========================
        # Orders
        # ==========================

        financial["total_orders"] = int(
            len(df)
        )

        # ==========================
        # Revenue Per Customer
        # ==========================

        customer_column = None

        for col in df.columns:

            column = col.lower()

            if any(
                keyword in column
                for keyword in [
                    "customer",
                    "client",
                    "buyer"
                ]
            ):
                customer_column = col
                break

        if customer_column and revenue_column:

            customer_count = df[
                customer_column
            ].nunique()

            if customer_count > 0:

                financial[
                    "revenue_per_customer"
                ] = round(
                    float(
                        df[revenue_column].sum()
                        / customer_count
                    ),
                    2
                )

        return financial
    def _product_kpis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        product_kpis = {}

        product_column = None

        for col in df.columns:

            column = col.lower()

            if any(
                keyword in column
                for keyword in [
                    "product",
                    "item",
                    "sku"
                ]
            ):
                product_column = col
                break

        if product_column:

            top_product = (
                df[product_column]
                .value_counts()
                .idxmax()
            )

            product_kpis["top_product"] = str(
                top_product
            )

        return product_kpis
    
    def _category_kpis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        result = {}

        category_column = None

        for col in df.columns:

            column = col.lower()

            if "category" in column:
                category_column = col
                break

        if category_column:

            result["top_category"] = str(
                df[category_column]
                .value_counts()
                .idxmax()
            )

        return result
    def _region_kpis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        result = {}

        region_column = None

        for col in df.columns:

            column = col.lower()

            if any(
                keyword in column
                for keyword in [
                    "region",
                    "country",
                    "state",
                    "location"
                ]
            ):
                region_column = col
                break

        if region_column:

            result["top_region"] = str(
                df[region_column]
                .value_counts()
                .idxmax()
            )

        return result
    
    