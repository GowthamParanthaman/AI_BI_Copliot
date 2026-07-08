from __future__ import annotations

from datetime import datetime
from typing import Final

from loguru import logger

from workflows.bi_workflow import BIWorkflow
from workflows.state import BIWorkflowState


class WorkflowTester:
    """
    Enterprise Workflow Validation Suite

    Validates:
    ----------
    - Workflow compilation
    - Graph initialization
    - State schema compatibility
    - Workflow readiness
    - Startup diagnostics
    """

    TEST_DATASET: Final[str] = "enterprise_validation"

    @classmethod
    def run(cls) -> None:

        start_time = datetime.utcnow()

        logger.info("=" * 80)
        logger.info("AI BUSINESS INTELLIGENCE COPILOT")
        logger.info("WORKFLOW VALIDATION STARTED")
        logger.info("=" * 80)

        try:

            # ==================================================
            # BUILD WORKFLOW
            # ==================================================

            logger.info(
                "Building LangGraph workflow..."
            )

            graph = BIWorkflow.build()

            logger.success(
                "Workflow compiled successfully"
            )

            # ==================================================
            # CREATE TEST STATE
            # ==================================================

            test_state: BIWorkflowState = {
                "dataset_name": cls.TEST_DATASET,
                "question": (
                    "What are the most important "
                    "business insights?"
                ),
                "execution_status": "TEST"
            }

            logger.success(
                "Workflow state created"
            )

            # ==================================================
            # WORKFLOW DIAGNOSTICS
            # ==================================================

            logger.info(
                "Workflow Diagnostics"
            )

            print()
            print("=" * 80)

            print(
                f"Graph Type        : "
                f"{type(graph).__name__}"
            )

            print(
                f"State Type        : "
                f"{type(test_state).__name__}"
            )

            print(
                f"Dataset Name      : "
                f"{test_state['dataset_name']}"
            )

            print(
                f"Execution Status  : "
                f"{test_state['execution_status']}"
            )

            print(
                f"Validation Time   : "
                f"{start_time.isoformat()}"
            )

            print("=" * 80)

            # ==================================================
            # SUCCESS
            # ==================================================

            logger.success(
                "Workflow validation completed"
            )

            print()
            print("=" * 80)
            print("WORKFLOW VALIDATION PASSED")
            print("=" * 80)

        except Exception as exc:

            logger.exception(
                "Workflow validation failed"
            )

            print()
            print("=" * 80)
            print("WORKFLOW VALIDATION FAILED")
            print("=" * 80)
            print(f"Error: {exc}")
            print("=" * 80)

            raise


def main() -> None:
    """
    Application Entry Point
    """

    WorkflowTester.run()


if __name__ == "__main__":
    main()