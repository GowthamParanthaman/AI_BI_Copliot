from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from datetime import datetime
from time import perf_counter

from typing import Any

from loguru import logger

from workflows.state import BIWorkflowState



class BaseAgent(ABC):
    """
    Enterprise Base Agent

    Features
    --------
    - Standardized execution lifecycle
    - Input validation
    - Output validation
    - Runtime metrics
    - Centralized logging
    - Error tracking
    - Workflow state management
    - LangGraph compatible

    Lifecycle
    ---------
    run()
        ├── validate_input()
        ├── execute()
        ├── validate_output()
        ├── metrics collection
        └── error handling
    """

    agent_name: str = "BaseAgent"

    agent_version: str = "1.0.0"

    # ==================================================
    # MAIN EXECUTION ENTRYPOINT
    # ==================================================

    def run(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        started_at = datetime.utcnow()

        start_time = perf_counter()

        logger.info(
            f"[{self.agent_name}] "
            f"Execution started"
        )

        try:

            # ======================================
            # INPUT VALIDATION
            # ======================================

            self.validate_input(
                state
            )

            # ======================================
            # BUSINESS LOGIC
            # ======================================

            result = self.execute(
                state
            )

            # ======================================
            # OUTPUT VALIDATION
            # ======================================

            self.validate_output(
                result
            )

            execution_time = round(
                perf_counter() - start_time,
                4
            )

            if "agent_metrics" not in result:
                result["agent_metrics"] = {}

            result["agent_metrics"][
                self.agent_name
            ] = {

                "status":
                    "SUCCESS",

                "agent":
                    self.agent_name,

                "version":
                    self.agent_version,

                "execution_time_seconds":
                    execution_time,

                "started_at":
                    started_at.isoformat(),

                "completed_at":
                    datetime.utcnow().isoformat()
            }

            logger.success(
                f"[{self.agent_name}] "
                f"Completed in "
                f"{execution_time}s"
            )

            return result

        except Exception as exc:

            execution_time = round(
                perf_counter() - start_time,
                4
            )

            logger.exception(
                f"[{self.agent_name}] "
                f"Execution failed"
            )

            errors = state.get("agent_errors")

            if errors is None:
                errors = []
                state["agent_errors"] = errors

            errors.append({

                "agent":
                    self.agent_name,

                "version":
                    self.agent_version,

                "error":
                    str(exc),

                "execution_time_seconds":
                    execution_time,

                "timestamp":
                    datetime.utcnow().isoformat()
            })

            state.setdefault(
                "agent_metrics",
                {}
            )

            metrics = state.get("agent_metrics")

            if metrics is None:
                metrics = {}
                state["agent_metrics"] = metrics

            metrics[self.agent_name] = {
                "status": "FAILED",
                "agent": self.agent_name,
                "version": self.agent_version,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            raise RuntimeError(
                f"{self.agent_name} failed: {exc}"
            ) from exc

    # ==================================================
    # ABSTRACT BUSINESS LOGIC
    # ==================================================

    @abstractmethod
    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:
        """
        Main business logic.

        Must be implemented
        by every agent.
        """
        raise NotImplementedError

    # ==================================================
    # VALIDATION HOOKS
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:
        """
        Override if agent requires
        custom input validation.
        """
        return None

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:
        """
        Override if agent requires
        custom output validation.
        """
        return None

    # ==================================================
    # METADATA
    # ==================================================

    @property
    def metadata(
        self
    ) -> dict[str, Any]:

        return {

            "agent_name":
                self.agent_name,

            "agent_version":
                self.agent_version,

            "agent_class":
                self.__class__.__name__
        }

    # ==================================================
    # STRING REPRESENTATION
    # ==================================================

    def __repr__(
        self
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(name={self.agent_name}, "
            f"version={self.agent_version})"
        )