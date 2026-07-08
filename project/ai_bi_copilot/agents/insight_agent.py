from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState

from llm.provider import LLMProvider
from llm.prompts import PromptRegistry


class InsightAgent(BaseAgent):
    """
    Enterprise Business Intelligence Insight Agent

    Responsibilities
    ----------------
    - Convert KPIs into business insights
    - Detect growth opportunities
    - Detect business risks
    - Generate executive observations
    - Generate strategic intelligence
    - Feed Recommendation Agent

    Input
    -----
    state["kpis"]
    state["analysis_results"]

    Output
    ------
    state["insights"]
    state["insight_metadata"]
    """

    agent_name = "InsightAgent"

    agent_version = "1.0.0"

    # ==================================================
    # EXECUTION ENTRYPOINT
    # ==================================================
    
    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting execution"
        )

        self.validate_input(state)

        start_time = datetime.utcnow()

        try:

            prompt = self._build_prompt(
                state
            )

            llm = (
                LLMProvider.get_model()
            )

            response = llm.invoke(
                prompt
            )

            analysis_results = state.get(
                "analysis_results",
                {}
            )

            business_insights = analysis_results.get(
                "business_insights",
                []
            )

            risks = []

            outlier_analysis = analysis_results.get(
                "outlier_analysis",
                {}
            )

            for column, data in outlier_analysis.items():

                if data.get("risk_level") == "HIGH":

                    risks.append(
                        f"High outlier risk detected in {column}"
                    )

            structured_insights = {

                "insights":
                    business_insights,

                "risks":
                    risks,

                "opportunities":
                    business_insights[:3],

                "executive_summary":
                    (
                        business_insights[0]
                        if business_insights
                        else "No insights generated."
                    ),

                "insight_count":
                    len(business_insights)
            }

            metadata = {

                "agent": self.agent_name,

                "version":
                    self.agent_version,

                "generated_at":
                    datetime.utcnow(),

                "model":
                    llm.model_name,

                "prompt_length":
                    len(prompt),

                "response_length":
                    len(
                        str(structured_insights)
                    )
            }

            state["insights"] = structured_insights

            state["insight_metadata"] = metadata

            state["insight_status"] = "COMPLETED"

            state["insight_started_at"] = (
                start_time.isoformat()
            )

            state["insight_completed_at"] = (
                datetime.utcnow().isoformat()
            )

            self.validate_output(
                state
            )

            logger.success(
                f"[{self.agent_name}] "
                f"Insights generated successfully"
            )

            return state

        except Exception as exc:

            logger.exception(
                f"[{self.agent_name}] Failed"
            )

            state["insight_status"] = "FAILED"

            state["insight_error"] = str(exc)

            raise RuntimeError(
                f"Insight generation failed: {exc}"
            ) from exc

    # ==================================================
    # INPUT VALIDATION
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "kpis",

            "analysis_results"
        ]

        missing = [

            field

            for field
            in required_fields

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
        state: BIWorkflowState
    ) -> None:

        if not state.get(
            "insights"
        ):

            raise RuntimeError(
                "Insight generation returned empty output"
            )

    # ==================================================
    # PROMPT BUILDER
    # ==================================================

    def _build_prompt(
        self,
        state: BIWorkflowState
    ) -> str:

        analysis_results = (
            state.get(
                "analysis_results",
                {}
            )
        )

        kpis = state.get(
            "kpis",
            {}
        )

        dataset_name = (
            state.get(
                "dataset_name",
                "Unknown Dataset"
            )
        )

        return PromptRegistry.get(

            PromptRegistry.INSIGHT_GENERATION,

            dataset_name=dataset_name,

            analysis_results=
                analysis_results,

            kpi_results=kpis
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
                "Business Intelligence"
        }