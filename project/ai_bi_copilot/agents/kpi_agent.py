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

        # Chart-ready arrays derived from the real DataFrame
        state["kpis"]["charts"] = self._compute_chart_data(df)

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

    # ==================================================
    # CHART DATA — real arrays from the DataFrame
    # ==================================================

    def _compute_chart_data(
        self,
        df,
    ):
        """
        Derive chart-ready arrays from actual DataFrame rows.
        No hardcoded seeds — every value comes from real data.
        """

        revenue_column = self._detect_column(
            df,
            ["revenue", "sales", "amount", "total_amount", "gross_sales", "net_sales", "income"],
        )

        date_column = self._detect_column(
            df,
            ["date", "order_date", "transaction_date", "created_at", "timestamp", "purchase_date"],
        )

        category_column = self._detect_column(
            df,
            ["category", "segment", "department"],
        )

        return {
            "revenue_by_period":        self._revenue_by_period(df, revenue_column, date_column, category_column),
            "revenue_trend":            self._revenue_trend(df, revenue_column, date_column),
            "category_distribution":    self._category_distribution(df, revenue_column, category_column),
            "order_value_distribution": self._order_value_distribution(df, revenue_column),
        }

    @staticmethod
    def _detect_column(df, keywords):
        for col in df.columns:
            if any(kw in str(col).lower().strip() for kw in keywords):
                return col
        return None

    def _revenue_by_period(self, df, revenue_column, date_column, category_column):
        """Quarterly revenue if date col, by category otherwise, equal splits as fallback."""
        import pandas as pd

        if revenue_column is None:
            return {}

        rev = pd.to_numeric(df[revenue_column], errors="coerce").fillna(0)

        if date_column:
            try:
                dates = pd.to_datetime(df[date_column], errors="coerce")
                work  = pd.DataFrame({"rev": rev, "date": dates}).dropna(subset=["date"])
                if not work.empty:
                    work["quarter"] = work["date"].dt.to_period("Q").astype(str)
                    grouped = work.groupby("quarter")["rev"].sum().sort_index()
                    if not grouped.empty:
                        logger.info(f"Revenue by quarter: {grouped.to_dict()}")
                        return {
                            "labels": list(grouped.index),
                            "values": [round(float(v), 2) for v in grouped.values],
                            "type":   "quarterly",
                        }
            except Exception as exc:
                logger.warning(f"Quarterly grouping failed: {exc}")

        if category_column:
            try:
                work    = pd.DataFrame({"rev": rev, "cat": df[category_column].astype(str)})
                grouped = work.groupby("cat")["rev"].sum().sort_values(ascending=False).head(6)
                if not grouped.empty:
                    logger.info(f"Revenue by category: {grouped.to_dict()}")
                    return {
                        "labels": list(grouped.index),
                        "values": [round(float(v), 2) for v in grouped.values],
                        "type":   "category",
                    }
            except Exception as exc:
                logger.warning(f"Category grouping failed: {exc}")

        n  = len(rev)
        qs = [float(rev.iloc[i * n // 4:(i + 1) * n // 4].sum()) for i in range(4)]
        return {
            "labels": ["Period 1", "Period 2", "Period 3", "Period 4"],
            "values": [round(v, 2) for v in qs],
            "type":   "period",
        }

    def _revenue_trend(self, df, revenue_column, date_column):
        """Real monthly revenue if date col exists, else 12 equal row-index slices."""
        import pandas as pd

        if revenue_column is None:
            return {}

        rev = pd.to_numeric(df[revenue_column], errors="coerce").fillna(0)

        if date_column:
            try:
                dates = pd.to_datetime(df[date_column], errors="coerce")
                work  = pd.DataFrame({"rev": rev, "date": dates}).dropna(subset=["date"])
                if not work.empty:
                    work["month"] = work["date"].dt.to_period("M")
                    grouped = work.groupby("month")["rev"].sum().sort_index()
                    if not grouped.empty:
                        logger.info(f"Monthly revenue: {len(grouped)} periods")
                        return {
                            "labels": [str(p) for p in grouped.index],
                            "values": [round(float(v), 2) for v in grouped.values],
                            "type":   "monthly",
                        }
            except Exception as exc:
                logger.warning(f"Monthly grouping failed: {exc}")

        n      = len(rev)
        slices = [float(rev.iloc[i * n // 12:(i + 1) * n // 12].sum()) for i in range(12)]
        return {
            "labels": [f"Period {i + 1}" for i in range(12)],
            "values": [round(v, 2) for v in slices],
            "type":   "period",
        }

    def _category_distribution(self, df, revenue_column, category_column):
        """Real category share as % of total revenue. Returns top-5 + Other."""
        import pandas as pd

        if category_column is None:
            return {}

        try:
            if revenue_column:
                rev    = pd.to_numeric(df[revenue_column], errors="coerce").fillna(0)
                totals = (
                    pd.DataFrame({"rev": rev, "cat": df[category_column].astype(str)})
                    .groupby("cat")["rev"]
                    .sum()
                    .sort_values(ascending=False)
                )
            else:
                totals = df[category_column].astype(str).value_counts().astype(float)

            grand = float(totals.sum())
            if grand == 0:
                return {}

            top5   = totals.head(5)
            other  = grand - float(top5.sum())
            labels = list(top5.index)
            values = [round(float(v) / grand * 100, 1) for v in top5.values]

            if other > 0:
                labels.append("Other")
                values.append(round(other / grand * 100, 1))

            logger.info(f"Category distribution: {dict(zip(labels, values))}")
            return {"labels": labels, "values": values}

        except Exception as exc:
            logger.warning(f"Category distribution failed: {exc}")
            return {}

    def _order_value_distribution(self, df, revenue_column):
        """Real histogram of per-row order values using fixed $100-wide bins."""
        import pandas as pd

        if revenue_column is None:
            return {}

        try:
            series = pd.to_numeric(df[revenue_column], errors="coerce").dropna()
            series = series[series > 0]
            if series.empty:
                return {}

            edges      = [0, 100, 200, 300, 400, 500, 600, 700, float("inf")]
            bin_labels = ["0-100", "100-200", "200-300", "300-400",
                          "400-500", "500-600", "600-700", "700+"]

            counts = (
                pd.cut(series, bins=edges, labels=bin_labels, right=False)
                .value_counts()
                .reindex(bin_labels, fill_value=0)
            )

            logger.info(f"Order value histogram: {counts.to_dict()}")
            return {
                "labels": bin_labels,
                "values": [int(v) for v in counts.values],
            }

        except Exception as exc:
            logger.warning(f"Order value distribution failed: {exc}")
            return {}

