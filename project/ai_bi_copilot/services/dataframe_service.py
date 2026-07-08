from __future__ import annotations

from typing import Any

import pandas as pd
import numpy as np

from loguru import logger


class DataFrameService:
    """
    Enterprise DataFrame Service

    Responsibilities
    ----------------
    - Schema inference
    - Dataset profiling
    - Memory optimization
    - Data quality assessment
    - Statistical analysis
    - Outlier detection
    - Business readiness scoring

    Used By
    -------
    - Upload API
    - File Storage Service
    - BI Workflow
    - Cleaning Agent
    - Schema Agent
    """

    # ==================================================
    # MASTER PROFILE
    # ==================================================

    def profile_dataframe(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        logger.info(
            "Generating enterprise dataframe profile"
        )

        profile = {

            "row_count":
                int(len(df)),

            "column_count":
                int(len(df.columns)),

            "memory_mb":
                self.memory_usage_mb(df),

            "quality_score":
                self.calculate_quality_score(df),

            "schema":
                self.get_schema(df),

            "missing_values":
                self.get_missing_values(df),

            "duplicate_rows":
                self.get_duplicate_count(df),

            "cardinality":
                self.get_cardinality(df),

            "numeric_profile":
                self.numeric_summary(df),

            "outliers":
                self.detect_outliers(df),

            "dataset_health":
                self.dataset_health(df)
        }

        logger.success(
            "Dataframe profile completed"
        )

        return profile

    # ==================================================
    # SCHEMA
    # ==================================================

    def get_schema(
        self,
        df: pd.DataFrame
    ) -> dict[str, str]:

        schema: dict[str, str] = {}

        for column, dtype in df.dtypes.items():

            schema[str(column)] = str(dtype)

        return schema

    # ==================================================
    # MISSING VALUES
    # ==================================================

    def get_missing_values(
        self,
        df: pd.DataFrame
    ) -> dict[str, int]:

        missing: dict[str, int] = {}

        for column, count in (
            df.isna()
            .sum()
            .items()
        ):

            missing[str(column)] = int(count)

        return missing

    # ==================================================
    # DUPLICATES
    # ==================================================

    def get_duplicate_count(
        self,
        df: pd.DataFrame
    ) -> int:

        return int(
            df.duplicated().sum()
        )

    # ==================================================
    # CARDINALITY
    # ==================================================

    def get_cardinality(
        self,
        df: pd.DataFrame
    ) -> dict[str, int]:

        return {

            column: int(
                df[column].nunique(
                    dropna=True
                )
            )

            for column in df.columns
        }

    # ==================================================
    # MEMORY
    # ==================================================

    def memory_usage_mb(
        self,
        df: pd.DataFrame
    ) -> float:

        return round(
            df.memory_usage(
                deep=True
            ).sum()
            / 1024
            / 1024,
            2
        )

    # ==================================================
    # MEMORY OPTIMIZATION
    # ==================================================

    def optimize_types(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        logger.info(
            "Optimizing dataframe memory usage"
        )

        optimized_df = df.copy()

        before_memory = self.memory_usage_mb(
            optimized_df
        )

        # Integer Downcast

        for column in optimized_df.select_dtypes(
            include=["int"]
        ).columns:

            optimized_df[column] = pd.to_numeric(
                optimized_df[column],
                downcast="integer"
            )

        # Float Downcast

        for column in optimized_df.select_dtypes(
            include=["float"]
        ).columns:

            optimized_df[column] = pd.to_numeric(
                optimized_df[column],
                downcast="float"
            )

        after_memory = self.memory_usage_mb(
            optimized_df
        )

        logger.success(
            f"Memory reduced "
            f"{before_memory}MB → "
            f"{after_memory}MB"
        )

        return optimized_df

    # ==================================================
    # QUALITY SCORE
    # ==================================================

    def calculate_quality_score(
        self,
        df: pd.DataFrame
    ) -> float:

        total_cells = max(
            len(df) * len(df.columns),
            1
        )

        missing_ratio = (
            df.isna().sum().sum()
            / total_cells
        )

        duplicate_ratio = (
            self.get_duplicate_count(df)
            / max(len(df), 1)
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

    # ==================================================
    # NUMERIC SUMMARY
    # ==================================================

    def numeric_summary(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        result: dict[str, Any] = {}

        numeric_columns = list(
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numeric_columns:

            result[column] = {

                "min":
                    float(df[column].min()),

                "max":
                    float(df[column].max()),

                "mean":
                    float(df[column].mean()),

                "median":
                    float(df[column].median()),

                "std":
                    float(df[column].std())
                    if len(df[column]) > 1
                    else 0.0,

                "variance":
                    float(df[column].var())
                    if len(df[column]) > 1
                    else 0.0
            }

        return result

    # ==================================================
    # OUTLIERS
    # ==================================================

    def detect_outliers(
        self,
        df: pd.DataFrame
    ) -> dict[str, int]:

        outliers: dict[str, int] = {}

        numeric_columns = (
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numeric_columns:

            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - (1.5 * iqr)
            upper = q3 + (1.5 * iqr)

            count = int(

                (
                    (df[column] < lower)
                    |
                    (df[column] > upper)
                ).sum()
            )

            outliers[column] = count

        return outliers

    # ==================================================
    # DATASET HEALTH
    # ==================================================

    def dataset_health(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        return {

            "quality_score":
                self.calculate_quality_score(df),

            "duplicate_rows":
                self.get_duplicate_count(df),

            "missing_cells":
                int(
                    df.isna()
                    .sum()
                    .sum()
                ),

            "memory_mb":
                self.memory_usage_mb(df),

            "business_ready":
                bool(self.calculate_quality_score(df)
                >= 85)
        }
    @staticmethod
    def make_json_safe(value):

        if isinstance(value, np.bool_):
            return bool(value)

        if isinstance(value, np.integer):
            return int(value)

        if isinstance(value, np.floating):
            return float(value)

        return value    