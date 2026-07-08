from __future__ import annotations

from typing import Any

import pandas as pd

from loguru import logger


class AnomalyService:

    def detect_anomalies(
        self,
        df: pd.DataFrame
    ) -> list[dict[str, Any]]:

        logger.info(
            "Starting anomaly detection"
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

            result = self._detect_iqr(
                df,
                column
            )

            if result:

                anomalies.append(
                    result
                )

        logger.success(
            f"Detected {len(anomalies)} anomalies"
        )

        return anomalies

    # ==================================================
    # IQR ANOMALY DETECTION
    # ==================================================

    def _detect_iqr(
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
            self._severity(
                anomaly_percentage
            )
        )

        return {

            "column":
                column,

            "anomaly_count":
                anomaly_count,

            "anomaly_percentage":
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
                ),

            "minimum":
                round(
                    float(series.min()),
                    2
                ),

            "maximum":
                round(
                    float(series.max()),
                    2
                )
        }

    # ==================================================
    # SEVERITY
    # ==================================================

    def _severity(
        self,
        percentage: float
    ) -> str:

        if percentage >= 15:

            return "HIGH"

        if percentage >= 5:

            return "MEDIUM"

        return "LOW"