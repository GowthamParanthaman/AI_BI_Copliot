from __future__ import annotations

from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

import pandas as pd
from loguru import logger

from workflows.bi_workflow import BIWorkflow
from workflows.state import BIWorkflowState
from typing import cast


class BIService:
    """
    Enterprise Business Intelligence Service

    Architecture
    ------------
    API Layer
        ↓
    BIService
        ↓
    LangGraph Workflow
        ↓
    Multi-Agent System
        ↓
    GPT-4o / OpenAI

    Responsibilities
    ----------------
    - Workflow orchestration
    - State initialization
    - Execution monitoring
    - Error handling
    - Performance tracking
    - Health diagnostics
    """

    _workflow = None

    def __init__(self) -> None:

        if BIService._workflow is None:

            logger.info(
                "Compiling Business Intelligence Workflow"
            )

            BIService._workflow = (
                BIWorkflow.build()
            )

            logger.success(
                "Workflow compilation completed"
            )

        self.workflow = BIService._workflow

    # =====================================================
    # PUBLIC API
    # =====================================================

    def run_pipeline(
        self,
        dataframe: pd.DataFrame,
        dataset_name: str,
        question: str | None = None
    ) -> BIWorkflowState:
        """
        Execute full Business Intelligence pipeline.
        """

        self._validate_inputs(
            dataframe=dataframe,
            dataset_name=dataset_name
        )

        execution_id = str(
            uuid4()
        )

        start_time = perf_counter()

        logger.info(
            f"[{execution_id}] "
            f"Pipeline execution started"
        )

        state: BIWorkflowState = {

            # =====================================
            # Execution Metadata
            # =====================================

            "execution_id":
                execution_id,

            "execution_status":
                "RUNNING",

            # =====================================
            # Dataset
            # =====================================

            "dataset_name":
                dataset_name,

            "dataframe":
                dataframe,

            # =====================================
            # User Input
            # =====================================

            "question":
                question or "",

            # =====================================
            # Monitoring
            # =====================================

            "agent_metrics":
                {},

            "agent_errors":
                []
        }

        try:

            result = cast(
                BIWorkflowState,
                self.workflow.invoke(state)
            )
            
            
            logger.info(
                f"Chart Paths = {result.get('chart_paths')}"
            )

            logger.info(
                f"Chart Count = {len(result.get('chart_paths', []))}"
            )
            
            logger.info(
                f"BIService chart_paths = {result.get('chart_paths')}"
            )

            execution_time = round(
                perf_counter() - start_time,
                4
            )

            result["execution_status"] = "SUCCESS"

            result["completed_at"] = (
                datetime.utcnow().isoformat()
            )

            result["execution_time_seconds"] = (
                execution_time
            )

            logger.success(
                f"[{execution_id}] "
                f"Pipeline completed in "
                f"{execution_time}s"
            )

            return result

        except Exception as exc:

            execution_time = round(
                perf_counter() - start_time,
                4
            )

            logger.exception(
                f"[{execution_id}] "
                f"Pipeline execution failed"
            )

            state.update({

                "execution_status":
                    "FAILED",

                "execution_time_seconds":
                    execution_time,

                "error":
                    str(exc)
            })

            raise RuntimeError(
                f"Pipeline execution failed: {exc}"
            ) from exc

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Service diagnostics.
        """

        return {

            "service":
                "BIService",

            "status":
                "HEALTHY",

            "workflow_ready":
                self.workflow is not None,

            "timestamp":
                datetime.utcnow().isoformat()
        }

    # =====================================================
    # INTERNALS
    # =====================================================

    @staticmethod
    def _validate_inputs(
        dataframe: pd.DataFrame,
        dataset_name: str
    ) -> None:
        """
        Validate incoming request.
        """

        if dataframe is None:

            raise ValueError(
                "dataframe cannot be None"
            )

        if not isinstance(
            dataframe,
            pd.DataFrame
        ):

            raise TypeError(
                "dataframe must be pandas DataFrame"
            )

        if dataframe.empty:

            raise ValueError(
                "dataframe is empty"
            )

        if not dataset_name:

            raise ValueError(
                "dataset_name is required"
            )

    # =====================================================
    # DIAGNOSTICS
    # =====================================================

    def get_service_info(
        self
    ) -> dict[str, Any]:
        """
        Service metadata.
        """

        return {

            "service":
                "BIService",

            "version":
                "1.0.0",

            "workflow":
                type(self.workflow).__name__,

            "architecture":
                "LangGraph Multi-Agent BI Copilot"
        }