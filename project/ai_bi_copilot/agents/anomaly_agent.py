from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from loguru import logger

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState


class AnomalyAgent(BaseAgent):

    agent_name = "AnomalyAgent"

    agent_version = "1.0.0"

    # ==================================================
    # INPUT VALIDATION
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        if "dataframe" not in state:

            raise ValueError(
                "dataframe missing from workflow state"
            )

    # ==================================================
    # EXECUTE
    # ==================================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting anomaly detection"
        )

        self.validate_input(
            state
        )

        df = state.get(
            "dataframe"
        )

        if df is None:

            raise ValueError(
                "dataframe missing"
            )

        anomalies = []

        numeric_columns = list(

            df.select_dtypes(
                include=["number"]
            ).columns
        )

        logger.info(
            f"Numeric Columns: {numeric_columns}"
        )

        for column in numeric_columns:

            result = self._detect_iqr_anomalies(
                df,
                column
            )

            if result:

                anomalies.append(
                    result
                )

        state["anomalies"] = (
            anomalies
        )

        state["anomaly_count"] = (
            len(anomalies)
        )

        state["anomaly_status"] = (
            "COMPLETED"
        )

        state[
            "anomaly_generated_at"
        ] = (
            datetime.utcnow()
            .isoformat()
        )

        logger.success(
            f"[{self.agent_name}] "
            f"Detected {len(anomalies)} anomalies"
        )

        return state

    # ==================================================
    # IQR DETECTION
    # ==================================================

    def _detect_iqr_anomalies(
        self,
        df: pd.DataFrame,
        column: str
    ) -> dict[str, Any] | None:

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        ).dropna()

        if len(series) < 5:

            return None

        q1 = series.quantile(
            0.25
        )

        q3 = series.quantile(
            0.75
        )

        iqr = q3 - q1

        lower_bound = (
            q1 - 1.5 * iqr
        )

        upper_bound = (
            q3 + 1.5 * iqr
        )

        anomaly_rows = series[

            (series < lower_bound)

            |

            (series > upper_bound)
        ]

        anomaly_count = len(
            anomaly_rows
        )

        if anomaly_count == 0:

            return None

        anomaly_percentage = round(

            (
                anomaly_count
                / len(series)
            ) * 100,

            2
        )

        severity = (
            self._calculate_severity(
                anomaly_percentage
            )
        )

        return {

            "column":
                column,

            "count":
                anomaly_count,

            "percentage":
                anomaly_percentage,

            "severity":
                severity,

            "lower_bound":
                round(
                    float(lower_bound),
                    2
                ),

            "upper_bound":
                round(
                    float(upper_bound),
                    2
                )
        }

    # ==================================================
    # SEVERITY
    # ==================================================

    def _calculate_severity(
        self,
        percentage: float
    ) -> str:

        if percentage >= 15:

            return "HIGH"

        if percentage >= 5:

            return "MEDIUM"

        return "LOW"