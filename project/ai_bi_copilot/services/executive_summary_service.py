from __future__ import annotations

from typing import Any

from loguru import logger


class ExecutiveSummaryService:

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def generate_summary(
        self,
        kpis: dict[str, Any],
        forecast_results: dict[str, Any],
        anomalies: list[dict[str, Any]],
        root_causes: dict[str, Any],
        recommendations: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Generating executive summary"
        )

        summary = []

        financial = kpis.get(
            "financial",
            {}
        )

        category = kpis.get(
            "category",
            {}
        )

        quality = kpis.get(
            "quality",
            {}
        )

        total_revenue = financial.get(
            "total_revenue",
            0
        )

        total_orders = financial.get(
            "total_orders",
            0
        )

        revenue_per_customer = (
            financial.get(
                "revenue_per_customer",
                0
            )
        )

        top_category = category.get(
            "top_category"
        )

        quality_score = quality.get(
            "quality_score",
            0
        )

        # ==================================
        # REVENUE
        # ==================================

        if total_revenue > 0:

            summary.append(

                f"Revenue reached "
                f"{total_revenue:,.2f}, "
                f"indicating active business performance."
            )

        # ==================================
        # ORDERS
        # ==================================

        if total_orders > 0:

            summary.append(

                f"The organization processed "
                f"{total_orders:,} orders."
            )

        # ==================================
        # CUSTOMER VALUE
        # ==================================

        if revenue_per_customer > 0:

            summary.append(

                f"Average customer value "
                f"was {revenue_per_customer:,.2f}."
            )

        # ==================================
        # CATEGORY
        # ==================================

        if top_category:

            summary.append(

                f"{top_category} remains "
                f"the strongest category."
            )

        # ==================================
        # FORECAST
        # ==================================

        if forecast_results.get(
            "forecast_available"
        ):

            growth_rate = (
                forecast_results.get(
                    "growth_rate",
                    0
                )
            )

            outlook = (
                forecast_results.get(
                    "business_outlook",
                    "UNKNOWN"
                )
            )

            next_90 = (
                forecast_results.get(
                    "next_90_days",
                    0
                )
            )

            summary.append(

                f"Revenue is forecasted "
                f"to change by "
                f"{growth_rate}% "
                f"over the next 90 days."
            )

            summary.append(

                f"Projected revenue "
                f"after 90 days is "
                f"{next_90:,.2f}."
            )

            summary.append(

                f"Business outlook "
                f"is {outlook}."
            )

        # ==================================
        # ANOMALIES
        # ==================================

        anomaly_count = len(
            anomalies
        )

        if anomaly_count > 0:

            high_risk = len([

                a

                for a in anomalies

                if a.get(
                    "severity"
                ) == self.HIGH
            ])

            summary.append(

                f"{anomaly_count} anomaly "
                f"patterns were detected."
            )

            if high_risk > 0:

                summary.append(

                    f"{high_risk} high-risk "
                    f"anomalies require "
                    f"immediate attention."
                )

        else:

            summary.append(

                "No significant anomalies "
                "were detected."
            )

        # ==================================
        # ROOT CAUSE
        # ==================================

        causes = root_causes.get(
            "root_causes",
            []
        )

        if causes:

            top_cause = causes[0]

            summary.append(

                f"Primary business driver: "
                f"{top_cause.get('cause')}."
            )

        # ==================================
        # RECOMMENDATIONS
        # ==================================

        high_priority = (
            recommendations.get(
                "high_priority",
                []
            )
        )

        if high_priority:

            summary.append(

                f"Top recommendation: "
                f"{high_priority[0]['recommendation']}."
            )

        # ==================================
        # DATA HEALTH
        # ==================================

        if quality_score >= 90:

            health_status = "EXCELLENT"

        elif quality_score >= 75:

            health_status = "GOOD"

        elif quality_score >= 50:

            health_status = "MODERATE"

        else:

            health_status = "CRITICAL"

        summary.append(

            f"Data quality health "
            f"is {health_status} "
            f"({quality_score}/100)."
        )

        # ==================================
        # CEO SUMMARY
        # ==================================

        executive_brief = " ".join(summary)

        result = {

            "executive_summary":
                summary,

            "executive_brief":
                executive_brief,

            "summary_count":
                len(summary),

            "health_status":
                health_status,

            "business_ready":
                quality_score >= 85
        }

        logger.success(

            f"Executive summary generated "
            f"with {len(summary)} insights"
        )

        return result