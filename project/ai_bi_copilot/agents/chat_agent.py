from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger

from agents.base_agent import BaseAgent

from llm.provider import LLMProvider
from workflows.state import BIWorkflowState

class ChatAgent(BaseAgent):
    """
    Enterprise Business Intelligence Chat Agent

    Responsibilities
    ----------------
    - Conversational BI Interface
    - KPI Explanation
    - Insight Exploration
    - Recommendation Justification
    - Executive Q&A
    - Context-Aware Responses

    Input
    -----
    state["question"]

    Output
    ------
    state["chat_response"]
    state["chat_metadata"]
    """

    agent_name = "ChatAgent"

    agent_version = "2.0.0"

    MAX_CONTEXT_LENGTH = 15000

    # ==================================================
    # EXECUTE
    # ==================================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Processing request"
        )

        self.validate_input(state)

        started_at = datetime.utcnow()

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

            answer = str(
                response.content
            ).strip()

            question = state.get(
                "question",
                ""
            )

            metadata = {

                "agent_name":
                    self.agent_name,

                "agent_version":
                    self.agent_version,

                "generated_at":
                    datetime.utcnow().isoformat(),

                "question_length":
                    len(question),

                "response_length":
                    len(answer)
            }

            history = state.get(
                "chat_history",
                []
            )

            history.append({

                "timestamp":
                    datetime.utcnow().isoformat(),

                "question":
                    question,

                "response":
                    answer
            })

            state["chat_response"] = answer

            state["chat_history"] = history

            state["chat_metadata"] = metadata

            state["chat_status"] = "COMPLETED"

            state["chat_started_at"] = (
                started_at.isoformat()
            )

            state["chat_completed_at"] = (
                datetime.utcnow().isoformat()
            )

            self.validate_output(
                state
            )

            logger.success(
                f"[{self.agent_name}] Response generated"
            )

            return state

        except Exception as exc:

            logger.exception(
                f"[{self.agent_name}] Failed"
            )

            state["chat_status"] = "FAILED"

            state["chat_error"] = str(exc)

            raise RuntimeError(
                f"Chat execution failed: {exc}"
            ) from exc

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        question = state.get(
            "question"
        )

        if not question:

            raise ValueError(
                "Question not found in workflow state"
            )

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        if not state.get(
            "chat_response"
        ):

            raise RuntimeError(
                "Empty LLM response"
            )

    # ==================================================
    # PROMPT BUILDER
    # ==================================================

    def _build_prompt(
        self,
        state: BIWorkflowState
    ) -> str:

        question = state.get(
            "question",
            ""
        )

        analysis_results = state.get(
            "analysis_results",
            {}
        )

        kpis = state.get(
            "kpis",
            {}
        )

        insights = state.get(
            "insights",
            ""
        )

        recommendations = state.get(
            "recommendations",
            ""
        )

        report = state.get(
            "report",
            ""
        )

        context = f"""
ANALYSIS RESULTS
{analysis_results}

KPIs
{kpis}

BUSINESS INSIGHTS
{insights}

RECOMMENDATIONS
{recommendations}

EXECUTIVE REPORT
{report}
"""

        context = context[
            : self.MAX_CONTEXT_LENGTH
        ]

        return f"""
You are an Enterprise AI Business Intelligence Copilot.

Your responsibilities:

1. Explain KPIs
2. Explain insights
3. Explain recommendations
4. Answer executive business questions
5. Provide data-driven responses
6. Never invent metrics
7. Only use supplied context

BUSINESS CONTEXT
================

{context}

USER QUESTION
=============

{question}

Provide:

1. Direct Answer

2. Supporting Evidence

3. Business Impact

4. Recommended Next Action

Respond professionally.
"""

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
                "Conversational BI Agent"
        }