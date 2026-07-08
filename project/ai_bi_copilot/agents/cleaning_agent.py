from __future__ import annotations
from datetime import datetime
from typing import Any

import pandas as pd

from loguru import logger

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState

class CleaningAgent(BaseAgent):
    """
    Enterprise Data Cleaning Agent

    ```
    Responsibilities
    ----------------
    - Column normalization
    - Missing value profiling
    - Duplicate analysis
    - Data type profiling
    - Cardinality analysis
    - Outlier detection
    - Data quality scoring
    - Cleaning report generation
    """

    agent_name = "CleaningAgent"
    agent_version = "2.0.0"

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        dataframe = state.get(
            "dataframe"
        )

        if dataframe is None:

            raise ValueError(
                "dataframe missing from workflow state"
            )

        if not isinstance(
            dataframe,
            pd.DataFrame
        ):

            raise TypeError(
                "dataframe must be a pandas DataFrame"
            )

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] "
            f"Starting cleaning workflow"
        )

        df = state.get("dataframe")

        if df is None:
            raise ValueError(
                "dataframe missing from workflow state"
            )

        original_rows = len(df)
        original_columns = len(df.columns)

        # =====================================
        # COLUMN STANDARDIZATION
        # =====================================

        df.columns = self._normalize_columns(
            df.columns
        )

        # =====================================
        # DUPLICATE ANALYSIS
        # =====================================

        duplicate_rows = int(
            df.duplicated().sum()
        )

        df = df.drop_duplicates()

        rows_after_dedup = len(df)

        # =====================================
        # MISSING VALUE ANALYSIS
        # =====================================

        missing_by_column = {
            column: int(count)
            for column, count
            in df.isna().sum().items()
        }

        missing_values_count = int(
            sum(
                missing_by_column.values()
            )
        )

        # =====================================
        # DATA TYPE PROFILING
        # =====================================

        data_types = {
            column: str(dtype)
            for column, dtype
            in df.dtypes.items()
        }

        # =====================================
        # CARDINALITY ANALYSIS
        # =====================================

        cardinality = {
            column: int(
                df[column].nunique(
                    dropna=True
                )
            )
            for column in df.columns
        }

        # =====================================
        # NUMERIC PROFILE
        # =====================================

        numeric_columns = list(
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        numeric_profile = {}

        for column in numeric_columns:

            numeric_profile[column] = {
                "min": float(
                    df[column].min()
                ) if not df[column].empty else 0,
                "max": float(
                    df[column].max()
                ) if not df[column].empty else 0,
                "mean": float(
                    df[column].mean()
                ) if not df[column].empty else 0
            }

        # =====================================
        # OUTLIER DETECTION
        # =====================================

        outlier_summary = (
            self._detect_outliers(df)
        )

        # =====================================
        # QUALITY SCORE
        # =====================================

        quality_score = (
            self._calculate_quality_score(
                total_rows=len(df),
                total_columns=len(df.columns),
                missing_values=missing_values_count,
                duplicate_rows=duplicate_rows
            )
        )

        # =====================================
        # CLEANING REPORT
        # =====================================

        cleaning_report = {

            "rows_before":
                original_rows,

            "rows_after":
                rows_after_dedup,

            "columns":
                original_columns,

            "duplicates_removed":
                duplicate_rows,

            "missing_values":
                missing_values_count,

            "quality_score":
                quality_score
        }

        # =====================================
        # UPDATE WORKFLOW STATE
        # =====================================

        state["dataframe"] = df

        state["cleaning_status"] = "COMPLETED"

        state["cleaned_at"] = (
            datetime.utcnow().isoformat()
        )

        state["duplicate_rows_count"] = duplicate_rows

        state["duplicate_rows_removed"] = duplicate_rows

        state["missing_values_count"] = (
            missing_values_count
        )

        state["missing_values_by_column"] = (
            missing_by_column
        )

        state["data_types"] = data_types

        state["cardinality"] = cardinality

        state["numeric_profile"] = (
            numeric_profile
        )

        state["outlier_summary"] = (
            outlier_summary
        )

        state["quality_score"] = quality_score

        state["cleaning_report"] = (
            cleaning_report
        )
        logger.success(
            f"[{self.agent_name}] "
            f"Completed | "
            f"Quality Score={quality_score}"
        )

        return state

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "dataframe",
            "cleaning_status",
            "quality_score",
            "cleaning_report"
        ]

        missing = [

            field
            for field in required_fields
            if field not in state
        ]

        if missing:

            raise RuntimeError(
                f"Missing output fields: {missing}"
            )

    @staticmethod
    def _normalize_columns(
        columns
    ) -> list[str]:

        return [

            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")

            for column in columns
        ]

    @staticmethod
    def _detect_outliers(
        df: pd.DataFrame
    ) -> dict[str, int]:

        result = {}

        numeric_columns = (
            df.select_dtypes(
                include=["number"]
            )
            .columns
        )

        for column in numeric_columns:

            q1 = df[column].quantile(
                0.25
            )

            q3 = df[column].quantile(
                0.75
            )

            iqr = q3 - q1

            lower = q1 - (
                1.5 * iqr
            )

            upper = q3 + (
                1.5 * iqr
            )

            outliers = df[
                (
                    df[column] < lower
                )
                |
                (
                    df[column] > upper
                )
            ]

            result[column] = len(
                outliers
            )

        return result

    @staticmethod
    def _calculate_quality_score(
        total_rows: int,
        total_columns: int,
        missing_values: int,
        duplicate_rows: int
    ) -> float:

        total_cells = max(
            total_rows * total_columns,
            1
        )

        missing_ratio = (
            missing_values /
            total_cells
        )

        duplicate_ratio = (
            duplicate_rows /
            max(total_rows, 1)
        )

        score = (
            100
            - (missing_ratio * 60)
            - (duplicate_ratio * 40)
        )

        return round(
            max(score, 0),
            2
        )

