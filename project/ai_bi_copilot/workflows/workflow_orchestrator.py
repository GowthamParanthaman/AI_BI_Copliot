from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from agents.email_agent import EmailAgent

from typing import Any

from uuid import uuid4



# =====================================================
# WORKFLOW STATISTICS
# =====================================================

@dataclass(slots=True)
class WorkflowStatistics:
    """
    Workflow execution statistics.
    """

    workflows_started: int = 0

    workflows_completed: int = 0

    workflows_failed: int = 0

    last_execution: datetime | None = None

    last_error: str | None = None


# =====================================================
# WORKFLOW HEALTH
# =====================================================

@dataclass(slots=True)
class WorkflowHealth:
    """
    Workflow health status.
    """

    status: str

    workflows_started: int

    workflows_completed: int

    workflows_failed: int

    last_error: str | None
    
@dataclass(slots=True)
class WorkflowState:
    """
    Current workflow execution state.
    """

    workflow_id: str | None = None

    current_step: str = "IDLE"

    status: str = "READY"

    started_at: datetime | None = None

    finished_at: datetime | None = None    
            


# =====================================================
# WORKFLOW ORCHESTRATOR
# =====================================================

class WorkflowOrchestrator:
    """
    Enterprise Workflow Orchestrator.

    Responsibilities
    ----------------
    - Coordinate workflow execution
    - Execute agents in correct order
    - Monitor workflow health
    - Track execution statistics
    - Handle failures gracefully

    Used By
    -------
    - FastAPI Routes
    - Scheduler
    - Dashboard
    """

    def __init__(
        self,
        email_agent: EmailAgent,
        analysis_agent: Any | None = None,
        report_agent: Any | None = None,
    ) -> None:

        logger.info(
            "Initializing WorkflowOrchestrator..."
        )

        self.email_agent = email_agent

        self.analysis_agent = analysis_agent

        self.report_agent = report_agent

        self.statistics = WorkflowStatistics()
        
        self.state = WorkflowState()

        logger.success(
            "WorkflowOrchestrator initialized successfully."
        )
        
    
        


    def _start_workflow(self) -> None:
        """
        Start a workflow execution.
        """

        self.state.workflow_id = str(uuid4())

        self.state.current_step = "STARTED"

        self.state.status = "RUNNING"

        self.state.started_at = datetime.utcnow()

        self.statistics.workflows_started += 1

        logger.info(
            f"Workflow {self.state.workflow_id} started."
        )    
        
    # =====================================================
    # FINISH WORKFLOW
    # =====================================================

    def _finish_workflow(self) -> None:
        """
        Finish workflow execution successfully.
        """

        self.state.current_step = "FINISHED"

        self.state.status = "COMPLETED"

        self.state.finished_at = datetime.utcnow()

        self.statistics.workflows_completed += 1

        self.statistics.last_execution = self.state.finished_at

        logger.success(
            f"Workflow {self.state.workflow_id} completed successfully."
        )    
        
    # =====================================================
    # FAIL WORKFLOW
    # =====================================================

    def _fail_workflow(
        self,
        error: Exception
    ) -> None:
        """
        Handle workflow failure.
        """

        self.state.current_step = "FAILED"

        self.state.status = "FAILED"

        self.state.finished_at = datetime.utcnow()

        self.statistics.workflows_failed += 1

        self.statistics.last_execution = self.state.finished_at

        self.statistics.last_error = str(error)

        logger.exception(
            f"Workflow {self.state.workflow_id} failed."
        )    
    # =====================================================
    # RUN WORKFLOW
    # =====================================================

    def run_workflow(
        self,
        recipient: str,
        subject: str,
        context: dict[str, Any]
    ) -> bool:
        """
        Execute the complete Business Intelligence workflow.
        """

        logger.info(
            "Starting Business Intelligence workflow."
        )

        try:

            # Start workflow
            self._start_workflow()

            # -----------------------------------------
            # Step 1 : Business Analysis
            # -----------------------------------------

            self.state.current_step = "BUSINESS_ANALYSIS"

            logger.info(
                "Executing Business Analysis..."
            )

            if self.analysis_agent is not None:

                # Future implementation
                # analysis = self.analysis_agent.analyze(...)
                pass

            # -----------------------------------------
            # Step 2 : Report Generation
            # -----------------------------------------

            self.state.current_step = "REPORT_GENERATION"

            logger.info(
                "Generating Executive Report..."
            )

            if self.report_agent is not None:

                # Future implementation
                # report = self.report_agent.generate(...)
                pass

            # -----------------------------------------
            # Step 3 : Email Delivery
            # -----------------------------------------

            self.state.current_step = "EMAIL_DELIVERY"

            logger.info(
                "Sending Executive Report..."
            )

            success = self.email_agent.send_executive_report(
                recipient=recipient,
                subject=subject,
                context=context
            )

            if not success:

                raise RuntimeError(
                    "Failed to send executive report."
                )

            # Finish workflow
            self._finish_workflow()

            return True

        except Exception as exc:

            self._fail_workflow(exc)

            return False    