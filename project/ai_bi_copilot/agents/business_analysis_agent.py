from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

from schemas.kpi_schema import KPIResult
from datetime import UTC
from schemas.business_analysis_schema import BusinessAnalysisResult





# =====================================================
# AGENT STATISTICS
# =====================================================

@dataclass(slots=True)
class BusinessAnalysisStatistics:

    analyses_started: int = 0

    analyses_completed: int = 0

    analyses_failed: int = 0

    last_execution: datetime | None = None

    last_error: str | None = None


# =====================================================
# AGENT HEALTH
# =====================================================

@dataclass(slots=True)
class BusinessAnalysisHealth:

    status: str

    analyses_started: int

    analyses_completed: int

    analyses_failed: int

    last_error: str | None
    
    



# =====================================================
# BUSINESS ANALYSIS AGENT
# =====================================================

class BusinessAnalysisAgent:
    """
    Enterprise Business Analysis Agent.

    Responsibilities
    ----------------
    - KPI analysis
    - Trend detection
    - Risk identification
    - Executive summary generation
    - Business recommendations

    Used By
    -------
    - WorkflowOrchestrator
    - ReportAgent
    """

    def __init__(self) -> None:

        logger.info(
            "Initializing BusinessAnalysisAgent..."
        )

        self.statistics = BusinessAnalysisStatistics()

        logger.success(
            "BusinessAnalysisAgent initialized successfully."
        )
    # =====================================================
    # PRIVATE ANALYSIS METHODS
    # =====================================================
    # =====================================================
    # BUSINESS HEALTH EVALUATION
    # =====================================================

    def _evaluate_business_health(
        self,
        kpis: KPIResult
    ) -> str:
        """
        Evaluate the overall business health based on KPIs.

        Returns
        -------
        str
            EXCELLENT
            GOOD
            FAIR
            CRITICAL
        """

        logger.info(
            "Evaluating business health."
        )

        score = 0

        revenue_growth = kpis.financial.revenue_growth

        profit_margin = kpis.financial.profit_margin

        customer_satisfaction = (
            kpis.customer.customer_satisfaction
        )

        churn_rate = (
            kpis.customer.customer_churn
        )

        # ==========================================
        # Revenue Growth
        # ==========================================

        if revenue_growth >= 20:
            score += 25
        elif revenue_growth >= 10:
            score += 20
        elif revenue_growth >= 5:
            score += 15
        else:
            score += 5

        # ==========================================
        # Profit Margin
        # ==========================================

        if profit_margin >= 25:
            score += 25
        elif profit_margin >= 15:
            score += 20
        elif profit_margin >= 10:
            score += 15
        else:
            score += 5

        # ==========================================
        # Customer Satisfaction
        # ==========================================

        if customer_satisfaction >= 90:
            score += 25
        elif customer_satisfaction >= 80:
            score += 20
        elif customer_satisfaction >= 70:
            score += 15
        else:
            score += 5

        # ==========================================
        # Customer Churn
        # ==========================================

        if churn_rate <= 5:
            score += 25
        elif churn_rate <= 10:
            score += 20
        elif churn_rate <= 20:
            score += 15
        else:
            score += 5

        logger.info(
            f"Business Health Score: {score}/100"
        )

        if score >= 90:
            return "EXCELLENT"

        if score >= 75:
            return "GOOD"

        if score >= 50:
            return "FAIR"

        return "CRITICAL"

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    def _generate_executive_summary(
        self,
        kpis: KPIResult
    ) -> str:
        """
        Generate an executive business summary.
        """

        logger.info(
            "Generating executive summary."
        )

        business_health = self._evaluate_business_health(
            kpis
        )

        revenue_growth = kpis.financial.revenue_growth

        profit_margin = kpis.financial.profit_margin

        customer_satisfaction = (
            kpis.customer.customer_satisfaction
        )

        customer_churn = (
            kpis.customer.customer_churn
        )

        summary = (
            f"Business Health: {business_health}. "
            f"Revenue growth is {revenue_growth:.1f}%, "
            f"profit margin is {profit_margin:.1f}%, "
            f"customer satisfaction is {customer_satisfaction:.1f}%, "
            f"and customer churn is {customer_churn:.1f}%. "
        )

        if business_health == "EXCELLENT":

            summary += (
                "Overall business performance is outstanding with strong "
                "financial growth and excellent customer metrics."
            )

        elif business_health == "GOOD":

            summary += (
                "Business performance is healthy with stable growth. "
                "Focus on continuous improvement and customer retention."
            )

        elif business_health == "FAIR":

            summary += (
                "Business performance is acceptable but several key "
                "metrics require attention to sustain long-term growth."
            )

        else:

            summary += (
                "Business performance is critical. Immediate corrective "
                "actions are recommended to improve financial and customer KPIs."
            )

        logger.success(
            "Executive summary generated successfully."
        )

        return summary


    # =====================================================
    # IDENTIFY BUSINESS RISKS
    # =====================================================

    def _identify_risks(
        self,
        kpis: KPIResult
    ) -> list[str]:
        """
        Identify business risks from KPI values.
        """

        logger.info(
            "Identifying business risks."
        )

        risks: list[str] = []

        if kpis.financial.revenue_growth < 5:

            risks.append(
                "Revenue growth is below the expected target."
            )

        if kpis.financial.profit_margin < 10:

            risks.append(
                "Profit margin is critically low."
            )

        if kpis.customer.customer_satisfaction < 75:

            risks.append(
                "Customer satisfaction is declining."
            )

        if kpis.customer.customer_churn > 15:

            risks.append(
                "Customer churn rate is high."
            )

        if not risks:

            risks.append(
                "No significant business risks detected."
            )

        logger.success(
            f"Identified {len(risks)} business risks."
        )

        return risks


    # =====================================================
    # IDENTIFY OPPORTUNITIES
    # =====================================================

    def _identify_opportunities(
        self,
        kpis: KPIResult
    ) -> list[str]:
        """
        Identify business opportunities.
        """

        logger.info(
            "Identifying business opportunities."
        )

        opportunities: list[str] = []

        if kpis.financial.revenue_growth >= 15:

            opportunities.append(
                "Strong revenue growth can support market expansion."
            )

        if kpis.financial.profit_margin >= 20:

            opportunities.append(
                "Healthy profit margins allow further investment."
            )

        if kpis.customer.customer_satisfaction >= 90:

            opportunities.append(
                "High customer satisfaction strengthens brand loyalty."
            )

        if kpis.customer.customer_churn <= 5:

            opportunities.append(
                "Low customer churn indicates excellent customer retention."
            )

        if not opportunities:

            opportunities.append(
                "No major growth opportunities identified."
            )

        logger.success(
            f"Identified {len(opportunities)} opportunities."
        )

        return opportunities

    # =====================================================
    # GENERATE RECOMMENDATIONS
    # =====================================================

    def _generate_recommendations(
        self,
        kpis: KPIResult
    ) -> list[str]:
        """
        Generate business recommendations based on KPI values.
        """

        logger.info(
            "Generating business recommendations."
        )

        recommendations: list[str] = []

        revenue_growth = kpis.financial.revenue_growth

        profit_margin = kpis.financial.profit_margin

        customer_satisfaction = (
            kpis.customer.customer_satisfaction
        )

        customer_churn = (
            kpis.customer.customer_churn
        )

        # ==========================================
        # Revenue
        # ==========================================

        if revenue_growth < 10:

            recommendations.append(
                "Increase revenue through new customer acquisition and targeted marketing campaigns."
            )

        # ==========================================
        # Profit
        # ==========================================

        if profit_margin < 15:

            recommendations.append(
                "Improve profit margins by optimizing operational costs and pricing strategies."
            )

        # ==========================================
        # Customer Satisfaction
        # ==========================================

        if customer_satisfaction < 85:

            recommendations.append(
                "Improve customer satisfaction by enhancing product quality and customer support."
            )

        # ==========================================
        # Customer Churn
        # ==========================================

        if customer_churn > 10:

            recommendations.append(
                "Launch customer retention initiatives to reduce churn."
            )

        # ==========================================
        # High Performing Business
        # ==========================================

        if not recommendations:

            recommendations.append(
                "Maintain current strategy while exploring expansion opportunities."
            )

        logger.success(
            f"Generated {len(recommendations)} recommendations."
        )

        return recommendations
    
    # =====================================================
    # ANALYZE BUSINESS
    # =====================================================



    def analyze(
        self,
        kpis: KPIResult
    ) -> BusinessAnalysisResult:
        """
        Execute complete business analysis.
        """

        logger.info(
            "Starting business analysis."
        )

        self.statistics.analyses_started += 1

        try:

            health = self._evaluate_business_health(
                kpis
            )

            summary = self._generate_executive_summary(
                kpis
            )

            risks = self._identify_risks(
                kpis
            )

            opportunities = self._identify_opportunities(
                kpis
            )

            recommendations = (
                self._generate_recommendations(
                    kpis
                )
            )

            result = BusinessAnalysisResult(

                business_health=health,

                executive_summary=summary,

                recommendations=recommendations,

                risks=risks,

                opportunities=opportunities,

                kpis=kpis,

                generated_at=datetime.now(UTC)

            )

            self.statistics.analyses_completed += 1

            self.statistics.last_execution = (
                datetime.utcnow()
            )

            logger.success(
                "Business analysis completed successfully."
            )

            return result

        except Exception as exc:

            self.statistics.analyses_failed += 1

            self.statistics.last_error = str(exc)

            logger.exception(
                "Business analysis failed."
            )

            raise