from __future__ import annotations

from typing import Any

from loguru import logger


class InsightService:
    """
    Enterprise Insight Engine

    Generates:

    - KPI Insights
    - Trend Insights
    - Risk Signals
    - Opportunity Signals
    - Executive Summary
    """

    def generate_insights(
        self,
        kpis: dict[str, Any],
        analysis: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Generating enterprise insights"
        )

        insights = []

        risks = []

        opportunities = []

        insights.extend(
            self._generate_kpi_insights(
                kpis
            )
        )

        trend_result = (
            self._generate_trend_insights(
                analysis
            )
        )

        insights.extend(
            trend_result["insights"]
        )

        risks.extend(
            trend_result["risks"]
        )

        opportunities.extend(
            trend_result["opportunities"]
        )

        insights.extend(
            self._generate_anomaly_insights(
                analysis
            )
        )

        insights.extend(
            self._generate_quality_insights(
                analysis
            )
        )

        executive_summary = (
            self._generate_executive_summary(
                insights
            )
        )

        logger.success(
            f"{len(insights)} insights generated"
        )

        return {

            "insights":
                insights,

            "risks":
                risks,

            "opportunities":
                opportunities,

            "executive_summary":
                executive_summary,

            "insight_count":
                len(insights)
        }

    # ==========================================
    # KPI INSIGHTS
    # ==========================================

    def _generate_kpi_insights(
        self,
        kpis: dict[str, Any]
    ) -> list[str]:

        results = []

        financial = kpis.get(
            "financial",
            {}
        )

        if financial:

            if "total_revenue" in financial:

                results.append(
                    f"Total revenue generated is "
                    f"${financial['total_revenue']:,.2f}"
                )

            if "average_order_value" in financial:

                results.append(
                    f"Average order value is "
                    f"${financial['average_order_value']:,.2f}"
                )

            if "total_orders" in financial:

                results.append(
                    f"Total orders processed: "
                    f"{financial['total_orders']:,}"
                )

            if "revenue_per_customer" in financial:

                results.append(
                    f"Revenue per customer is "
                    f"${financial['revenue_per_customer']:,.2f}"
                )

        category = kpis.get(
            "category",
            {}
        )

        if category:

            top_category = category.get(
                "top_category"
            )

            if top_category:

                results.append(
                    f"Top performing category is "
                    f"{top_category}."
                )

        operational = kpis.get(
            "operational",
            {}
        )

        if "total_quantity" in operational:

            results.append(
                f"Total units sold: "
                f"{operational['total_quantity']:,}"
            )

        quality = kpis.get(
            "quality",
            {}
        )

        if "quality_score" in quality:

            results.append(
                f"Dataset quality score is "
                f"{quality['quality_score']}%."
            )

        return results

    # ==========================================
    # TREND INSIGHTS
    # ==========================================

    def _generate_trend_insights(
        self,
        analysis: dict[str, Any]
    ) -> dict[str, Any]:

        insights = []

        risks = []

        opportunities = []

        trends = analysis.get(
            "trend_analysis",
            {}
        )

        for column, trend in trends.items():

            if trend == "UPWARD":

                insights.append(
                    f"{column} is showing positive growth."
                )

                opportunities.append(
                    f"Capitalize on growing {column}."
                )

            elif trend == "DOWNWARD":

                insights.append(
                    f"{column} is declining."
                )

                risks.append(
                    f"Investigate decline in {column}."
                )

        return {

            "insights":
                insights,

            "risks":
                risks,

            "opportunities":
                opportunities
        }

    # ==========================================
    # ANOMALY INSIGHTS
    # ==========================================

    def _generate_anomaly_insights(
        self,
        outlier_analysis: dict
    ) -> list[str]:

        insights: list[str] = []

        if not outlier_analysis:
            return insights

        for column, anomaly_data in outlier_analysis.items():

            if not isinstance(
                anomaly_data,
                dict
            ):
                continue

            count = anomaly_data.get(
                "outlier_count",
                0
            )

            percentage = anomaly_data.get(
                "outlier_percentage",
                0.0
            )

            if count > 0:

                insights.append(
                    f"{column} contains "
                    f"{count} anomalies "
                    f"({percentage:.2f}% of records)"
                )

        return insights
        logger.info(
        f"Outlier Analysis: {outlier_analysis}"
    )

    # ==========================================
    # DATA QUALITY
    # ==========================================

    def _generate_quality_insights(
        self,
        analysis: dict[str, Any]
    ) -> list[str]:

        results = []

        readiness = analysis.get(
            "business_readiness",
            {}
        )

        score = readiness.get(
            "score",
            0
        )

        if score >= 90:

            results.append(
                "Dataset quality is excellent."
            )

        elif score >= 80:

            results.append(
                "Dataset quality is acceptable for BI."
            )

        else:

            results.append(
                "Dataset quality requires improvement."
            )

        return results

    # ==========================================
    # EXECUTIVE SUMMARY
    # ==========================================

    def _generate_executive_summary(
        self,
        insights: list[str]
    ) -> str:

        if not insights:

            return (
                "No significant business insights detected."
            )

        return (
            f"Generated {len(insights)} business insights. "
            f"Key finding: {insights[0]}"
        )