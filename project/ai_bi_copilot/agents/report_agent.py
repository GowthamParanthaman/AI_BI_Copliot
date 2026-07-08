from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from schemas.business_analysis_schema import BusinessAnalysisResult

from loguru import logger

from agents.base_agent import BaseAgent

from llm.provider import LLMProvider
from llm.prompts import PromptRegistry
from datetime import UTC

from schemas.report_schema import (
    ExecutiveReport,
    ReportHeader,
    KPISection,
    BusinessSection,
    TrendSection,
    RiskSection,
    OpportunitySection,
    RecommendationSection,
    VisualizationSection,
    ReportFooter,
)

from workflows.state import BIWorkflowState

from schemas.kpi_schema import KPIResult

from services.report_renderer import ReportRenderer

from services.pdf_exporter import PDFExporter


class ReportAgent(BaseAgent):
    """
    Enterprise Executive Report Agent

    Responsibilities
    ----------------
    - Executive Summary Generation
    - KPI Reporting
    - Business Insight Reporting
    - Recommendation Reporting
    - Executive Decision Support

    Inputs
    ------
    state["analysis_results"]
    state["kpis"]
    state["insights"]
    state["recommendations"]

    Outputs
    -------
    state["report"]
    state["report_metadata"]
    """

    agent_name = "ReportAgent"

    agent_version = "1.0.0"
    def _build_report(
        self,
        state: BIWorkflowState
    ) -> ExecutiveReport:
        """
        Build a structured executive report.
        """
        return ExecutiveReport(

            header=ReportHeader(

                title="Executive Business Report",

                company_name="AI BI Copilot",

                dataset_name=state.get(
                    "dataset_name",
                    "Unknown Dataset",
                ),

                generated_at=datetime.now(UTC),
            ),

            executive_summary=
                self._build_executive_summary(state),

            kpis=
                self._build_kpi_section(state),

            business=
                self._build_business_section(state),

            trends=
                self._build_trend_section(state),

            risks=
                self._build_risk_section(state),

            opportunities=
                self._build_opportunity_section(state),

            recommendations=
                self._build_recommendation_section(state),

            visualizations=
                self._build_visualization_section(state),

            executive_decision=
                "Proceed with the recommended strategic initiatives.",

            footer=
                self._build_footer(state),

            generated_at=datetime.now(UTC),
        )
        
    
    # ==========================================
    # EXECUTIVE SUMMARY
    # ==========================================

    def _build_executive_summary(
        self,
        state: BIWorkflowState,
    ) -> str:

        analysis = cast(
            BusinessAnalysisResult,
            state.get("business_analysis"),
        )

        kpi = cast(
            KPIResult,
            state.get("kpi_result"),
        )

        return f"""
Business Health : {kpi.health.business_health}

Revenue Growth : {kpi.financial.revenue_growth:.2f}%

Profit Margin : {kpi.financial.profit_margin:.2f}%

Customer Satisfaction :
{kpi.customer.customer_satisfaction:.2f}

Customer Churn :
{kpi.customer.customer_churn:.2f}%

Executive Summary

{analysis.executive_summary}
""".strip()

    
    # ==================================================
    # KPI SECTION
    # ==================================================

    def _build_kpi_section(
        self,
        state: BIWorkflowState,
    ) -> KPISection:

        kpi = cast(
            KPIResult,
            state.get("kpi_result"),
        )

        return KPISection(

            total_revenue=
                kpi.financial.total_revenue or 0.0,

            total_profit=
                kpi.financial.total_profit or 0.0,

            revenue_growth=
                kpi.financial.revenue_growth or 0.0,

            profit_margin=
                kpi.financial.profit_margin or 0.0,

            customer_count=
                kpi.customer.customer_count,

            customer_satisfaction=
                kpi.customer.customer_satisfaction or 0.0,

            customer_churn=
                kpi.customer.customer_churn or 0.0,

            average_order_value=
                kpi.customer.average_order_value or 0.0,

            top_product=
                kpi.product.top_product,

            top_region=
                kpi.region.top_region,
        )

    # ==================================================
    # BUSINESS SECTION
    # ==================================================

    def _build_business_section(
        self,
        state: BIWorkflowState,
    ) -> BusinessSection:

        analysis = cast(
            BusinessAnalysisResult,
            state.get("business_analysis"),
        )

        kpi = cast(
            KPIResult,
            state.get("kpi_result"),
        )

        return BusinessSection(

            health=
                kpi.health.business_health,

            executive_summary=
                analysis.executive_summary,

            key_findings=
                state.get(
                    "business_insights",
                    [],
                ),

            risks=
                analysis.risks,

            opportunities=
                analysis.opportunities,

            recommendations=
                analysis.recommendations,
        )

    # ==================================================
    # TREND SECTION
    # ==================================================

    def _build_trend_section(
        self,
        state: BIWorkflowState,
    ) -> TrendSection:

        return TrendSection(

            trends=
                state.get(
                    "business_insights",
                    [],
                )
        )

    # ==================================================
    # RISK SECTION
    # ==================================================

    def _build_risk_section(
        self,
        state: BIWorkflowState,
    ) -> RiskSection:

        analysis = cast(
            BusinessAnalysisResult,
            state.get("business_analysis"),
        )

        return RiskSection(

            critical=
                analysis.risks,

            medium=[],

            low=[],
        )

    # ==================================================
    # OPPORTUNITY SECTION
    # ==================================================

    def _build_opportunity_section(
        self,
        state: BIWorkflowState,
    ) -> OpportunitySection:

        analysis = cast(
            BusinessAnalysisResult,
            state.get("business_analysis"),
        )

        return OpportunitySection(

            opportunities=
                analysis.opportunities
        )

    # ==================================================
    # RECOMMENDATION SECTION
    # ==================================================

    def _build_recommendation_section(
        self,
        state: BIWorkflowState,
    ) -> RecommendationSection:

        analysis = cast(
            BusinessAnalysisResult,
            state.get("business_analysis"),
        )

        return RecommendationSection(

            strategic=
                analysis.recommendations,

            operational=
                state.get(
                    "operational_actions",
                    [],
                ),

            automation=
                state.get(
                    "automation_candidates",
                    [],
                ),
        )

    # ==================================================
    # VISUALIZATION SECTION
    # ==================================================

    def _build_visualization_section(
        self,
        state: BIWorkflowState,
    ) -> VisualizationSection:

        return VisualizationSection(

            charts=
                state.get(
                    "visualizations",
                    [],
                )
        )

    # ==================================================
    # FOOTER
    # ==================================================

    def _build_footer(
        self,
        state: BIWorkflowState,
    ) -> ReportFooter:

        return ReportFooter(

            generated_by="AI BI Copilot",

            model=
                state.get(
                    "llm_model",
                    "Unknown",
                ),

            version=
                self.agent_version,

            generated_at=
                datetime.now(UTC),
        )    

    # ==================================================
    # EXECUTION
    # ==================================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting report generation"
        )

        self.validate_input(state)

        started_at = datetime.now(UTC)

        try:
            
            structured_report = self._build_report(
                state
            )

            state["structured_report"] = structured_report

            prompt = self._build_prompt(
                structured_report
            )

            llm = LLMProvider.get_model()

            response = llm.invoke(
                prompt
            )

            report = (
                str(response.content)
                .strip()
            )

            renderer = ReportRenderer()

            markdown_report = renderer.to_markdown(
                structured_report
            )

            html_report = renderer.to_html(
                structured_report
            )
            
            chart_paths = state.get("chart_paths", [])

            logger.info("=" * 80)
            logger.info(f"Chart Paths: {chart_paths}")
            logger.info(f"Chart Count: {len(chart_paths)}")
            logger.info("=" * 80)

            pdf_exporter = PDFExporter()

            pdf_path = pdf_exporter.export(
                markdown_report,
                chart_paths=chart_paths,
            )
            
            from pathlib import Path

            logger.info(f"PDF Path: {pdf_path}")

            logger.info(f"PDF Exists: {Path(pdf_path).exists()}")

            logger.info(f"Chart Count: {len(state.get('chart_paths', []))}")

            logger.info(f"Charts: {state.get('chart_paths')}")


            

            metadata = {

                "agent_name":
                    self.agent_name,

                "agent_version":
                    self.agent_version,

                "generated_at":
                    datetime.now(UTC),

                "prompt_length":
                    len(prompt),

                "report_length":
                    len(report),

                "word_count":
                    len(report.split()),

                "line_count":
                    len(report.splitlines()),

                "estimated_read_time":
                    max(
                        1,
                        len(report.split()) // 200,
                    ),
            }

            state["report"] = report

            # Save the markdown version for future HTML/PDF export
            state["report_markdown"] = markdown_report

            state["report_html"] = html_report

            state["report_metadata"] = metadata

            state["report_status"] = "COMPLETED"

            state["report_started_at"] = started_at.isoformat()

            state["report_completed_at"] = datetime.now(UTC).isoformat()
            
            state["report_pdf_path"] = pdf_path

            self.validate_output(
                state
            )

            logger.success(
                f"[{self.agent_name}] Report generated successfully"
            )

            return state
            logger.info(
                f"Chart Paths = {state.get('chart_paths')}"
            )

            logger.info(
                f"Chart Metadata = {state.get('chart_metadata')}"
            )

        except Exception as exc:

            logger.exception(
                f"[{self.agent_name}] Failed"
            )

            state["report_status"] = "FAILED"

            state["report_error"] = str(exc)

            raise RuntimeError(
                f"Report generation failed: {exc}"
            ) from exc

    # ==================================================
    # INPUT VALIDATION
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "business_analysis",

            "dataset_name",
        ]

        missing = [

            field

            for field in required_fields

            if field not in state
        ]

        if missing:

            raise ValueError(
                f"Missing workflow fields: {missing}"
            )

    # ==================================================
    # OUTPUT VALIDATION
    # ==================================================

    def validate_output(
        self,
        state: BIWorkflowState,
    ) -> None:

        report = state.get("report")

        if not report:

            raise RuntimeError(
                "Generated report is empty."
            )

        if len(report.strip()) < 300:

            raise RuntimeError(
                "Generated report is unexpectedly short."
            )

    # ==================================================
    # PROMPT BUILDER
    # ==================================================

    def _build_prompt(
        self,
        report: ExecutiveReport,
    ) -> str:

        return PromptRegistry.get(

            PromptRegistry.REPORT_GENERATION,

            dataset_name=
                report.header.dataset_name,

            executive_summary=
                report.executive_summary,

            business_health=
                report.business.health,

            key_findings="\n".join(
                report.business.key_findings
            ),

            trends="\n".join(
                report.trends.trends
            ),

            risks="\n".join(
                report.risks.critical
            ),

            opportunities="\n".join(
                report.opportunities.opportunities
            ),

            strategic_recommendations="\n".join(
                report.recommendations.strategic
            ),

            operational_recommendations="\n".join(
                report.recommendations.operational
            ),

            automation_recommendations="\n".join(
                report.recommendations.automation
            ),

            executive_decision=
                report.executive_decision,
        )

    # ==================================================
    # AGENT INFO
    # ==================================================

    def get_agent_info(
        self
    ) -> dict[str, str]:

        return {

            "agent_name":
                self.agent_name,

            "agent_version":
                self.agent_version,

            "agent_type":
                "Executive Report Generator"
        }