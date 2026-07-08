from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from loguru import logger

from schemas.business_analysis_schema import BusinessAnalysisResult


class ExecutiveDashboardService:

    def build_dashboard(
        self,
        kpis: dict[str, Any],
        forecast: dict[str, Any],
        anomalies: list[dict[str, Any]],
        root_causes: dict[str, Any],
        health_score: dict[str, Any],
        alerts: dict[str, Any],
        recommendations: dict[str, Any],
        action_plan: dict[str, Any],
        executive_summary: dict[str, Any] | str,
        business_analysis: BusinessAnalysisResult,
    ) -> dict[str, Any]:

        logger.info("Building executive dashboard")
        logger.info(f"executive_summary type: {type(executive_summary)}")
        logger.info(f"business_analysis generated_at: {business_analysis.generated_at}")

        analysis_kpis = business_analysis.kpis
        financial = analysis_kpis.financial
        customer = analysis_kpis.customer
        product = analysis_kpis.product
        region = analysis_kpis.region
        kpi_health = analysis_kpis.health

        growth_rate = forecast.get("growth_rate", financial.revenue_growth)
        quality_score = customer.customer_satisfaction
        business_health_status = business_analysis.business_health

        executive_scorecard = {
            "Revenue": (
                "GOOD"
                if financial.total_revenue > 100000
                else "AT_RISK"
            ),
            "Profitability": (
                "GOOD"
                if financial.profit_margin >= 20
                else "STABLE"
                if financial.profit_margin >= 10
                else "AT_RISK"
            ),
            "Growth": (
                "GOOD"
                if growth_rate > 10
                else "STABLE"
                if growth_rate > 0
                else "AT_RISK"
            ),
            "Customer": (
                "EXCELLENT"
                if quality_score >= 90
                else "GOOD"
                if quality_score >= 75
                else "AT_RISK"
            ),
            "Health": business_health_status,
        }

        executive_brief = (
            business_analysis.executive_summary
            or (
                f"Revenue reached ${financial.total_revenue:,.0f} "
                f"with ${financial.total_profit:,.0f} in profit and a "
                f"{financial.profit_margin:.1f}% profit margin. "
                f"{product.top_category} is the leading category, "
                f"supported by {product.top_product} as the top product. "
                f"Business health is {business_health_status}."
            )
        )

        dashboard = {
            "dashboard_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "analysis_generated_at": business_analysis.generated_at.isoformat(),
                "dashboard_version": "3.0.0",
                "dashboard_type": "Executive Dashboard",
            },
            "executive_summary": {
                "business_health": business_health_status,
                "summary": executive_brief,
                "generated_at": business_analysis.generated_at.isoformat(),
            },
            "executive_scorecard": executive_scorecard,
            "executive_kpis": {
                "financial": {
                    "total_revenue": financial.total_revenue,
                    "total_profit": financial.total_profit,
                    "profit_margin": financial.profit_margin,
                    "revenue_growth": financial.revenue_growth,
                },
                "customer": {
                    "customer_count": customer.customer_count,
                    "customer_satisfaction": customer.customer_satisfaction,
                    "customer_churn": customer.customer_churn,
                    "average_order_value": customer.average_order_value,
                },
                "product": {
                    "top_product": product.top_product,
                    "top_category": product.top_category,
                    "total_products": product.total_products,
                },
                "region": {
                    "top_region": region.top_region,
                    "total_regions": region.total_regions,
                },
                "health": {
                    "business_health": kpi_health.business_health,
                    "score": kpi_health.score,
                },
            },
            "business_health": {
                "status": business_health_status,
                "kpi_status": kpi_health.business_health,
                "kpi_score": kpi_health.score,
                "reported_at": business_analysis.generated_at.isoformat(),
            },
            "forecast_center": {
                "forecast_available": forecast.get("forecast_available", False),
                "growth_rate": growth_rate,
                "next_30_days": forecast.get("next_30_days", 0),
                "next_60_days": forecast.get("next_60_days", 0),
                "next_90_days": forecast.get("next_90_days", 0),
                "business_outlook": forecast.get("business_outlook", "UNKNOWN"),
            },
            "alert_center": {
                "alert_count": alerts.get("alert_count", 0),
                "high_alerts": alerts.get("high_alerts", 0),
                "medium_alerts": alerts.get("medium_alerts", 0),
                "alerts": alerts.get("alerts", []),
            },
            "risk_center": {
                "risk_count": len(business_analysis.risks),
                "risks": business_analysis.risks,
                "anomalies": anomalies,
            },
            "opportunity_center": {
                "opportunity_count": len(business_analysis.opportunities),
                "opportunities": business_analysis.opportunities,
            },
            "root_cause_center": {
                "root_cause_count": root_causes.get("root_cause_count", 0),
                "root_causes": root_causes.get("root_causes", []),
            },
            "action_center": {
                "action_count": action_plan.get("action_count", 0),
                "executive_roadmap": action_plan.get("executive_roadmap", []),
                "action_plan": action_plan.get("action_plan", []),
            },
            "recommendation_center": {
                "recommendation_count": len(business_analysis.recommendations),
                "recommendations": business_analysis.recommendations,
                "supporting_recommendations": {
                    "recommendation_count": recommendations.get(
                        "recommendation_count",
                        0,
                    ),
                    "high_priority": recommendations.get("high_priority", []),
                    "medium_priority": recommendations.get("medium_priority", []),
                    "low_priority": recommendations.get("low_priority", []),
                },
            },
            "what_happens_next": {
                "next_30_days": forecast.get("next_30_days", 0),
                "next_60_days": forecast.get("next_60_days", 0),
                "next_90_days": forecast.get("next_90_days", 0),
                "growth_rate": growth_rate,
                "outlook": forecast.get("business_outlook", "UNKNOWN"),
            },
            "dashboard_status": {
                "business_health": business_health_status,
                "kpi_health": kpi_health.business_health,
                "kpi_score": kpi_health.score,
                "last_analysis_at": business_analysis.generated_at.isoformat(),
            },
        }

        logger.success("Executive dashboard generated successfully")

        return dashboard
