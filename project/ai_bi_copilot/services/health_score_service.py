from __future__ import annotations

from typing import Any

from loguru import logger


class HealthScoreService:

    def calculate(
        self,
        kpis: dict[str, Any],
        forecast_results: dict[str, Any],
        anomalies: list[dict[str, Any]],
        root_causes: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Calculating business health score"
        )

        financial = kpis.get(
            "financial",
            {}
        )

        quality = kpis.get(
            "quality",
            {}
        )

        # ==================================
        # QUALITY SCORE (30%)
        # ==================================

        quality_score = float(
            quality.get(
                "quality_score",
                100
            )
        )

        quality_component = (
            quality_score * 0.30
        )

        # ==================================
        # FORECAST SCORE (25%)
        # ==================================

        growth_rate = float(
            forecast_results.get(
                "growth_rate",
                0
            )
        )

        if growth_rate >= 20:

            forecast_score = 100

        elif growth_rate >= 10:

            forecast_score = 85

        elif growth_rate >= 0:

            forecast_score = 70

        else:

            forecast_score = 40

        forecast_component = (
            forecast_score * 0.25
        )

        # ==================================
        # ANOMALY SCORE (20%)
        # ==================================

        high_anomalies = len([

            anomaly

            for anomaly in anomalies

            if anomaly.get(
                "severity"
            ) == "HIGH"
        ])

        medium_anomalies = len([

            anomaly

            for anomaly in anomalies

            if anomaly.get(
                "severity"
            ) == "MEDIUM"
        ])

        anomaly_score = max(

            100
            - (high_anomalies * 15)
            - (medium_anomalies * 7),

            0
        )

        anomaly_component = (
            anomaly_score * 0.20
        )

        # ==================================
        # ROOT CAUSE SCORE (10%)
        # ==================================

        causes = root_causes.get(
            "root_causes",
            []
        )

        high_impact_causes = len([

            cause

            for cause in causes

            if cause.get(
                "impact"
            ) == "HIGH"
        ])

        root_cause_score = max(

            100
            - (high_impact_causes * 10),

            0
        )

        root_cause_component = (
            root_cause_score * 0.10
        )

        # ==================================
        # REVENUE SCORE (15%)
        # ==================================

        revenue = float(
            financial.get(
                "total_revenue",
                0
            )
        )

        if revenue >= 1_000_000:

            revenue_score = 100

        elif revenue >= 500_000:

            revenue_score = 85

        elif revenue >= 100_000:

            revenue_score = 70

        else:

            revenue_score = 50

        revenue_component = (
            revenue_score * 0.15
        )

        # ==================================
        # FINAL SCORE
        # ==================================

        final_score = round(

            quality_component
            + forecast_component
            + anomaly_component
            + root_cause_component
            + revenue_component,

            2
        )

        # ==================================
        # STATUS
        # ==================================

        if final_score >= 90:

            status = "EXCELLENT"

        elif final_score >= 75:

            status = "HEALTHY"

        elif final_score >= 60:

            status = "STABLE"

        elif final_score >= 40:

            status = "AT_RISK"

        else:

            status = "CRITICAL"

        result = {

            "business_health_score":
                final_score,

            "status":
                status,

            "score_breakdown": {

                    "quality_score":
                        round(
                            quality_component,
                            2
                        ),

                    "forecast_score":
                        round(
                            forecast_component,
                            2
                        ),

                    "anomaly_score":
                        round(
                            anomaly_component,
                            2
                        ),

                    "root_cause_score":
                        round(
                            root_cause_component,
                            2
                        ),

                    "revenue_score":
                        round(
                            revenue_component,
                            2
                        )
            },

            "quality_score":
                quality_score,

            "growth_rate":
                growth_rate,

            "high_anomalies":
                high_anomalies,

            "medium_anomalies":
                medium_anomalies,

            "high_impact_causes":
                high_impact_causes
        }

        logger.success(

            f"Business Health Score: "
            f"{final_score}/100 "
            f"({status})"
        )

        return result