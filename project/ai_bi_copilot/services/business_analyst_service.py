from typing import Any

from loguru import logger



class BusinessAnalystService:

    def analyze(
        self,
        kpis: dict[str, Any],
        forecast: dict[str, Any],
        anomalies: list[dict[str, Any]],
        root_causes: dict[str, Any],
        health_score: dict[str, Any],
        alerts: dict[str, Any],
        action_plan: dict[str, Any]
    ) -> dict[str, Any]:

        logger.info(
            "Generating business analyst report"
        )

        executive_assessment = []

        risks = []

        opportunities = []

        strategic_decisions = []

        next_actions = []

        focus_areas = []
    
        # ==================================
        # KPI ANALYSIS
        # ==================================

        financial = kpis.get(
            "financial",
            {}
        )

        revenue = financial.get(
            "total_revenue",
            0
        )
        
        if revenue > 300000:

            opportunities.append(

                "Expand high-performing product categories."
            )

            opportunities.append(

                "Increase inventory allocation for top sellers."
            )

        if revenue > 500000:

            opportunities.append(

                "Launch premium product offerings."
            )

        revenue_per_customer = (
            financial.get(
                "revenue_per_customer",
                0
            )
        )

        if revenue > 500000:

            executive_assessment.append(
                "Revenue performance is strong."
            )

            opportunities.append(
                "Scale high-performing products."
            )

        elif revenue > 100000:

            executive_assessment.append(
                "Revenue performance is stable."
            )

        else:

            risks.append(
                "Revenue is below expected threshold."
            )

        if revenue_per_customer > 500:

            opportunities.append(
                "Customer value is high."
            )

        # ==================================
        # FORECAST ANALYSIS
        # ==================================

        growth_rate = forecast.get(
            "growth_rate",
            0
        )

        if growth_rate > 15:

            opportunities.append(
                "Business growth forecast is strong."
            )

            strategic_decisions.append(
                "Increase investment in growth initiatives."
            )

            focus_areas.append(
                "Revenue Expansion"
            )

        elif growth_rate < 0:

            risks.append(
                "Revenue decline is forecasted."
            )

            strategic_decisions.append(
                "Review sales and marketing strategy."
            )

        # ==================================
        # ANOMALY ANALYSIS
        # ==================================

        high_anomalies = len([
            anomaly
            for anomaly in anomalies
            if anomaly.get("severity")
            == "HIGH"
        ])

        medium_anomalies = len([
            anomaly
            for anomaly in anomalies
            if anomaly.get("severity")
            == "MEDIUM"
        ])

        if high_anomalies > 0:

            risks.append(
                f"{high_anomalies} high-risk anomalies detected."
            )

            focus_areas.append(
                "Risk Mitigation"
            )

        # ==================================
        # ROOT CAUSE ANALYSIS
        # ==================================

        causes = root_causes.get(
            "root_causes",
            []
        )

        if causes:

            top_cause = causes[0]

            executive_assessment.append(

                f"Primary business driver: "
                f"{top_cause.get('cause')}."
            )

        # ==================================
        # HEALTH SCORE ANALYSIS
        # ==================================

        score = health_score.get(
            "business_health_score",
            100
        )

        status = health_score.get(
            "status",
            "UNKNOWN"
        )

        executive_assessment.append(

            f"Business Health Score: "
            f"{score}/100 ({status})"
        )

        if score < 60:

            risks.append(
                "Overall business health requires attention."
            )

            focus_areas.append(
                "Operational Excellence"
            )

        # ==================================
        # ALERT ANALYSIS
        # ==================================

        if alerts.get(
            "high_alerts",
            0
        ) > 0:

            risks.append(
                "Critical alerts require immediate action."
            )

        # ==================================
        # ACTION PLAN ANALYSIS
        # ==================================

        for action in action_plan.get(
            "action_plan",
            []
        )[:5]:

            next_actions.append(
                action.get(
                    "action"
                )
            )

        # ==================================
        # MARKET EXPANSION SIGNAL
        # ==================================

        if revenue > 500000:

            focus_areas.append(
                "Market Expansion"
            )

        # ==================================
        # REMOVE DUPLICATES
        # ==================================

        risks = list(
            dict.fromkeys(risks)
        )

        opportunities = list(
            dict.fromkeys(opportunities)
        )

        strategic_decisions = list(
            dict.fromkeys(
                strategic_decisions
            )
        )

        focus_areas = list(
            dict.fromkeys(
                focus_areas
            )
        )

        # ==================================
        # BUSINESS RISK ENGINE
        # ==================================

        alert_count = (

            alerts.get(
                "high_alerts",
                0
            )

            +

            alerts.get(
                "medium_alerts",
                0
            )
        )

        risk_score = min(

            100,

            (

                high_anomalies * 25

                +

                medium_anomalies * 10

                +

                alert_count * 5
            )
        )

        # ==================================
        # RISK LEVEL
        # ==================================

        if risk_score >= 70:

            risk_level = "HIGH"

        elif risk_score >= 40:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # ==================================
        # OPPORTUNITY SCORE
        # ==================================

        opportunity_score = min(

            100,

            len(opportunities) * 20
        )

        # ==================================
        # FORECAST SCORE
        # ==================================

        forecast_outlook = forecast.get(
            "business_outlook",
            "STABLE"
        )

        if forecast_outlook == "POSITIVE":

            forecast_score = 100

        elif forecast_outlook == "STABLE":

            forecast_score = 70

        else:

            forecast_score = 40

        # ==================================
        # DECISION CONFIDENCE
        # ==================================

        decision_confidence = round(

            (

                score * 0.40

                +

                opportunity_score * 0.25

                +

                forecast_score * 0.20

                +

                (100 - risk_score) * 0.15

            ),

            2
        )
        
        # ==================================
        # EXECUTIVE DECISION
        # ==================================

        executive_decision = (

            self._generate_executive_decision(

                revenue=revenue,

                growth_rate=growth_rate,

                risk_score=risk_score,

                opportunity_score=opportunity_score,

                health_score=score,

                forecast_outlook=forecast.get(
                    "business_outlook",
                    "STABLE"
                )
            )
        )
        executive_decision["confidence"] = (
            decision_confidence
        )

        # ==================================
        # EXECUTIVE STATUS
        # ==================================

        if score >= 85:

            executive_status = (
                "HIGH PERFORMING"
            )

        elif score >= 70:

            executive_status = (
                "GROWTH STAGE"
            )

        elif score >= 50:

            executive_status = (
                "STABLE"
            )

        else:

            executive_status = (
                "AT RISK"
            )

        # ==================================
        # MANAGEMENT BRIEF
        # ==================================

        management_brief = {

            "health_status":
                executive_status,

            "top_risk":
                risks[0]
                if risks
                else "None",

            "top_opportunity":
                opportunities[0]
                if opportunities
                else "None",

            "next_priority":
                next_actions[0]
                if next_actions
                else "None"
        }

        # ==================================
        # BUSINESS READINESS
        # ==================================

        business_ready = (

            score >= 75

            and

            risk_score <= 30

            and

            forecast_outlook != "NEGATIVE"
        )

        # ==================================
        # FINAL RESULT
        # ==================================

        result = {

            "executive_assessment":
                executive_assessment,

            "management_brief":
                management_brief,
            
            "executive_decision":
                executive_decision,
    
            "risk_matrix": {

                "HIGH":

                    [

                        risk

                        for risk in risks

                        if "critical" in risk.lower()

                        or "high" in risk.lower()
                    ],

                "MEDIUM":

                    [

                        risk

                        for risk in risks

                        if "medium" in risk.lower()
                    ],

                "LOW":

                    [

                        risk

                        for risk in risks

                        if (

                            "critical"

                            not in risk.lower()

                            and

                            "high"

                            not in risk.lower()

                            and

                            "medium"

                            not in risk.lower()
                        )
                    ]
            },

            "opportunity_ranking":

                [

                    {

                        "rank":
                            index + 1,

                        "opportunity":
                            opportunity,

                        "impact":

                            "HIGH"

                            if index == 0

                            else "MEDIUM",

                        "priority":

                            "HIGH"

                            if index == 0

                            else "MEDIUM",

                        "estimated_roi":

                            "18%"

                            if index == 0

                            else "10%",

                        "confidence":

                            90

                            if index == 0

                            else 80

                    }

                    for index, opportunity

                    in enumerate(

                        opportunities
                    )
                ],

            "strategic_decisions":
                strategic_decisions,

            "focus_areas":
                focus_areas,

            "next_actions":
                next_actions,

            "business_readiness": {

                "status":

                    "READY"

                    if business_ready

                    else "NOT READY",

                "score":
                    score,

                "deployment":

                    "APPROVED"

                    if business_ready

                    else "REVIEW REQUIRED",

                "reason":

                    "Business health is excellent and operational risk is low."

                    if business_ready

                    else "Business requires improvements before expansion."
            },

            "executive_status":
                executive_status,

            "risk_score":
                risk_score,
            
            "risk_level":
                risk_level,    

            "opportunity_score":
                opportunity_score,

            "decision_confidence":
                decision_confidence,

            "risk_count":
                len(risks),

            "opportunity_count":
                len(opportunities),

            "high_anomalies":
                high_anomalies,

            "medium_anomalies":
                medium_anomalies
        }

        logger.success(

            f"Business analysis completed "
            f"({len(risks)} risks, "
            f"{len(opportunities)} opportunities)"
        )

        return result
    
    def _generate_executive_decision(
        self,
        revenue: float,
        growth_rate: float,
        risk_score: int,
        opportunity_score: int,
        health_score: float,
        forecast_outlook: str
    ) -> dict[str, Any]:

        # ==================================
        # DEFAULT VALUES
        # ==================================

        decision = "MONITOR BUSINESS"

        priority = "MEDIUM"

        expected_roi = "8%"

        confidence = 70.0

        reason = (
            "Business performance is stable."
        )

        # ==================================
        # EXPAND BUSINESS
        # ==================================

        if (

            revenue >= 500000

            and

            growth_rate >= 10

            and

            risk_score <= 20

            and

            health_score >= 85

        ):

            decision = "EXPAND BUSINESS"

            priority = "HIGH"

            expected_roi = "18%"

            confidence = 92.5

            reason = (
                "Revenue is strong, forecast is positive, "
                "business health is excellent, and risk is low."
            )

        # ==================================
        # INVEST IN GROWTH
        # ==================================

        elif (

            opportunity_score >= 80

            and

            health_score >= 80

        ):

            decision = "INVEST IN GROWTH"

            priority = "HIGH"

            expected_roi = "15%"

            confidence = 88.0

            reason = (
                "Business opportunities are strong "
                "with healthy operational performance."
            )

        # ==================================
        # OPTIMIZE OPERATIONS
        # ==================================

        elif (

            growth_rate >= 0

            and

            risk_score <= 40

        ):

            decision = "OPTIMIZE OPERATIONS"

            priority = "MEDIUM"

            expected_roi = "10%"

            confidence = 82.0

            reason = (
                "Business is stable. Focus on operational "
                "efficiency before expansion."
            )

        # ==================================
        # COST OPTIMIZATION
        # ==================================

        elif (

            growth_rate < 0

            or

            forecast_outlook == "NEGATIVE"

        ):

            decision = "COST OPTIMIZATION"

            priority = "HIGH"

            expected_roi = "5%"

            confidence = 90.0

            reason = (
                "Revenue growth is declining and "
                "forecast indicates increased business risk."
            )

        return {

            "decision":
                decision,

            "priority":
                priority,

            "confidence":
                confidence,

            "expected_roi":
                expected_roi,

            "reason":
                reason
        }