from __future__ import annotations

from typing import Any

from loguru import logger


class RecommendationService:

    HIGH_PRIORITY = "HIGH"
    MEDIUM_PRIORITY = "MEDIUM"
    LOW_PRIORITY = "LOW"

    def generate_recommendations(
        self,
        insights: list[str],
        kpis: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Generating strategic recommendations"
        )

        high_priority = []

        medium_priority = []

        low_priority = []

        executive_actions = []

        operational_actions = []

        automation_candidates = []
        financial = kpis.get(
            "financial",
            {}
        )

        category = kpis.get(
            "category",
            {}
        )

        operational = kpis.get(
            "operational",
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

        top_category = category.get(
            "top_category"
        )

        total_quantity = operational.get(
            "total_quantity",
            0
        )

        # ==================================
        # KPI-DRIVEN BUSINESS RULES
        # ==================================

        if total_revenue > 100000:

            high_priority.append({

                "recommendation":
                    "Increase investment in top-performing products",

                "priority":
                    self.HIGH_PRIORITY,

                "impact":
                    "HIGH",

                "timeline":
                    "30-60 days"
            })

            executive_actions.append(
                "Invest in growth initiatives"
            )

        if top_category:

            high_priority.append({

                "recommendation":
                    f"Increase inventory allocation for {top_category}",

                "priority":
                    self.HIGH_PRIORITY,

                "impact":
                    "HIGH",

                "timeline":
                    "30 days"
            })

        if total_orders > 500:

            medium_priority.append({

                "recommendation":
                    "Expand sales campaigns to sustain demand",

                "priority":
                    self.MEDIUM_PRIORITY,

                "impact":
                    "HIGH",

                "timeline":
                    "60-90 days"
            })

        if total_quantity > 1000:

            operational_actions.append(
                "Review inventory planning and supply chain capacity"
            )

        # ==================================
        # INSIGHT LOOP
        # ==================================

        for insight in insights:

            text = insight.lower()

            # ==================================
            # RISK
            # ==================================

            if any(
                word in text
                for word in [
                    "decline",
                    "downward",
                    "loss",
                    "anomaly",
                    "risk"
                ]
            ):

                high_priority.append({

                    "recommendation":
                        "Immediate investigation required",

                    "priority":
                        self.HIGH_PRIORITY,

                    "impact":
                        "HIGH",

                    "timeline":
                        "0-30 days"
                })

                executive_actions.append(
                    "Review declining KPI trends"
                )

            # ==================================
            # GROWTH
            # ==================================

            elif any(
                word in text
                for word in [
                    "growth",
                    "increase",
                    "profit",
                    "revenue",
                    "upward"
                ]
            ):

                medium_priority.append({

                    "recommendation":
                        "Scale successful strategy",

                    "priority":
                        self.MEDIUM_PRIORITY,

                    "impact":
                        "HIGH",

                    "timeline":
                        "30-90 days"
                })

                executive_actions.append(
                    "Invest in growth initiatives"
                )

            # ==================================
            # QUALITY
            # ==================================

            elif "quality" in text:

                low_priority.append({

                    "recommendation":
                        "Maintain governance framework",

                    "priority":
                        self.LOW_PRIORITY,

                    "impact":
                        "MEDIUM",

                    "timeline":
                        "Ongoing"
                })

        automation_candidates.extend([

            "Automated KPI Monitoring",

            "Automated Executive Reports",

            "Automated Revenue Alerts",

            "Automated Forecasting"
        ])

        # ==================================
        # REMOVE DUPLICATES
        # ==================================

        high_priority = list(
            {str(x): x for x in high_priority}.values()
        )

        medium_priority = list(
            {str(x): x for x in medium_priority}.values()
        )

        low_priority = list(
            {str(x): x for x in low_priority}.values()
        )

        result = {

            "high_priority":
                high_priority,

            "medium_priority":
                medium_priority,

            "low_priority":
                low_priority,

            "executive_actions":
                executive_actions,

            "operational_actions":
                operational_actions,

            "automation_candidates":
                automation_candidates,

            "recommendation_count":
                len(high_priority)
                + len(medium_priority)
                + len(low_priority)
        }

        logger.success(
            f"Generated "
            f"{result['recommendation_count']} "
            f"recommendations"
        )

        return result