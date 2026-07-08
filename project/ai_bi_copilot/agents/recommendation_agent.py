from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger

from agents.base_agent import BaseAgent

from llm.provider import LLMProvider
from llm.prompts import PromptRegistry
from datetime import UTC
from workflows.state import BIWorkflowState

class RecommendationAgent(BaseAgent):
    """
    Enterprise Recommendation Agent

    Responsibilities
    ----------------
    - Generate strategic recommendations
    - Generate revenue growth actions
    - Generate risk mitigation actions
    - Generate operational improvements
    - Generate executive next steps

    Inputs
    ------
    state["insights"]
    state["kpis"]
    state["analysis_results"]

    Outputs
    -------
    state["recommendations"]
    state["recommendation_metadata"]
    """

    agent_name = "RecommendationAgent"

    agent_version = "1.0.0"

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting recommendation generation"
        )

        self.validate_input(state)

        start_time = datetime.now(UTC)

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

            recommendations = {
                "summary": str(response.content).strip()
            }

            metadata = {

                "agent_name":
                    self.agent_name,

                "agent_version":
                    self.agent_version,

                "generated_at":
                    datetime.now(UTC),

                "prompt_length":
                    len(prompt),

                "response_length":
                    len(recommendations)
            }

            state["recommendations"] = recommendations

            state["recommendation_metadata"] = metadata

            state["recommendation_status"] = "COMPLETED"

            state["recommendation_started_at"] = (
                start_time.isoformat()
            )

            state["recommendation_completed_at"] = (
                datetime.now(UTC).isoformat()
            )

            self.validate_output(
                state
            )

            logger.success(
                f"[{self.agent_name}] Recommendations generated"
            )

            return state

        except Exception as exc:

            logger.exception(
                f"[{self.agent_name}] Failed"
            )

            state["recommendation_status"] = "FAILED"

            state["recommendation_error"] = str(exc)

            raise RuntimeError(
                f"Recommendation generation failed: {exc}"
            ) from exc

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "insights",

            "kpis"
        ]

        missing = [

            field

            for field in required_fields

            if field not in state
        ]

        if missing:

            raise ValueError(
                f"Missing required workflow fields: {missing}"
            )

    # =====================================================
    # OUTPUT VALIDATION
    # =====================================================

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        recommendations = state.get(
            "recommendations"
        )

        if not recommendations:

            raise RuntimeError(
                "Recommendation output is empty"
            )

    # =====================================================
    # PROMPT GENERATION
    # =====================================================

    def _build_prompt(
        self,
        state: BIWorkflowState
    ) -> str:

        insights = state.get(
            "insights",
            ""
        )

        kpis = state.get(
            "kpis",
            {}
        )

        analysis_results = state.get(
            "analysis_results",
            {}
        )

        dataset_name = state.get(
            "dataset_name",
            "Unknown Dataset"
        )

        return PromptRegistry.get(

            PromptRegistry.RECOMMENDATION_GENERATION,

            dataset_name=dataset_name,

            insights=insights,

            kpi_results=kpis,

            analysis_results=analysis_results
        )

    # =====================================================
    # AGENT INFO
    # =====================================================

    def get_agent_info(
        self
    ) -> dict[str, str]:

        return {

            "agent_name":
                self.agent_name,

            "agent_version":
                self.agent_version,

            "agent_type":
                "Business Recommendation Engine"
        }