from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from loguru import logger
from typing import Any, cast


class AnalysisService:
    """
    Enterprise Dataset Analysis Service
    """

    def analyze_dataset(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        logger.info(
            "Enterprise analysis started"
        )

        result = {

            "dataset_summary":
                self._dataset_summary(df),

            "descriptive_statistics":
                self._descriptive_statistics(df),

            "trend_analysis":
                self._trend_analysis(df),

            "anomaly_analysis":
                self._anomaly_analysis(df),

            "correlations":
                self._correlation_analysis(df),

            "top_categories":
                self._top_categories(df),

            "column_profiles":
                self._column_profiles(df),

            "business_readiness":
                self._business_readiness(df),

            "business_signals":
                self._business_signals(df)
        }

        logger.success(
            "Enterprise analysis completed"
        )

        return result

    # ==================================================
    # DATASET SUMMARY
    # ==================================================

    def _dataset_summary(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        return {

            "row_count":
                int(len(df)),

            "column_count":
                int(len(df.columns)),

            "numeric_columns":
                int(
                    len(
                        df.select_dtypes(
                            include="number"
                        ).columns
                    )
                ),

            "categorical_columns":
                int(
                    len(
                        df.select_dtypes(
                            include=["object", "category"]
                        ).columns
                    )
                ),

            "memory_usage_mb":
                round(
                    float(
                        df.memory_usage(
                            deep=True
                        ).sum()
                    ) / 1024 / 1024,
                    2
                )
        }

    # ==================================================
    # DESCRIPTIVE STATS
    # ==================================================

    def _descriptive_statistics(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        numeric_df = df.select_dtypes(
            include="number"
        )

        if numeric_df.empty:
            return {}

        stats = cast(
            dict[str, Any],
            numeric_df
            .describe()
            .round(2)
            .to_dict()
        )

        return stats

    # ==================================================
    # TREND ANALYSIS
    # ==================================================

    def _trend_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        trends = {}

        for column in (
            df.select_dtypes(
                include="number"
            ).columns
        ):

            values = (
                df[column]
                .dropna()
            )

            if len(values) < 2:
                continue

            first = float(values.iloc[0])
            last = float(values.iloc[-1])

            growth = round(
                (
                    (
                        last - first
                    )
                    / abs(first)
                ) * 100,
                2
            ) if first != 0 else 0

            trends[column] = {

                "direction":
                    (
                        "UPWARD"
                        if last > first
                        else (
                            "DOWNWARD"
                            if last < first
                            else "STABLE"
                        )
                    ),

                "growth_percent":
                    growth
            }

        return trends

    # ==================================================
    # ANOMALY ANALYSIS
    # ==================================================

    def _anomaly_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        anomalies = {}

        for column in (
            df.select_dtypes(
                include="number"
            ).columns
        ):

            values = (
                df[column]
                .dropna()
            )

            if len(values) < 10:
                continue

            std = values.std()

            if std == 0:
                continue

            z_scores = np.abs(
                (
                    values - values.mean()
                ) / std
            )

            count = int(
                (z_scores > 3).sum()
            )

            anomalies[column] = {

                "count":
                    count,

                "percentage":
                    round(
                        count
                        / len(values)
                        * 100,
                        2
                    )
            }

        return anomalies

    # ==================================================
    # CORRELATIONS
    # ==================================================

    def _correlation_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        numeric_df = df.select_dtypes(
            include="number"
        )

        if len(numeric_df.columns) < 2:
            return {}

        matrix = (
            numeric_df.corr(
                numeric_only=True
            )
        )

        strong = {}

        columns = list(
            matrix.columns
        )

        for i, col1 in enumerate(columns):

            for col2 in columns[i + 1:]:

                value = cast(
                    float,
                    matrix.loc[col1, col2]
                )

                corr = abs(value)

                if corr >= 0.70:

                    strong[
                        f"{col1}__{col2}"
                    ] = round(
                        corr,
                        4
                    )

        return strong

    # ==================================================
    # TOP CATEGORIES
    # ==================================================

    def _top_categories(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        result = {}

        for column in (
            df.select_dtypes(
                include=[
                    "object",
                    "category"
                ]
            ).columns
        ):

            result[column] = (
                df[column]
                .value_counts()
                .head(5)
                .to_dict()
            )

        return result

    # ==================================================
    # COLUMN PROFILES
    # ==================================================

    def _column_profiles(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        profiles = {}

        for column in df.columns:

            series = df[column]

            profiles[column] = {

                "dtype":
                    str(series.dtype),

                "null_percentage":
                    round(
                        float(
                            series.isna()
                            .mean()
                        ) * 100,
                        2
                    ),

                "unique_values":
                    int(
                        series.nunique()
                    ),

                "sample_values":
                    (
                        series
                        .dropna()
                        .astype(str)
                        .head(3)
                        .tolist()
                    )
            }

        return profiles

    # ==================================================
    # BUSINESS READINESS
    # ==================================================

    def _business_readiness(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        total_cells = max(
            len(df) * len(df.columns),
            1
        )

        missing = int(
            df.isna()
            .sum()
            .sum()
        )

        duplicates = int(
            df.duplicated()
            .sum()
        )

        score = round(
            max(
                100
                - (missing / total_cells) * 60
                - (duplicates / max(len(df), 1)) * 40,
                0
            ),
            2
        )

        return {

            "score":
                score,

            "missing_values":
                missing,

            "duplicate_rows":
                duplicates
        }

    # ==================================================
    # BUSINESS SIGNALS
    # ==================================================

    def _business_signals(
        self,
        df: pd.DataFrame
    ) -> dict[str, bool]:

        cols = " ".join(
            str(col).lower()
            for col in df.columns
        )

        return {

            "has_revenue":
                any(
                    x in cols
                    for x in [
                        "sales",
                        "revenue",
                        "amount",
                        "income"
                    ]
                ),

            "has_customer":
                any(
                    x in cols
                    for x in [
                        "customer",
                        "client"
                    ]
                ),

            "has_product":
                any(
                    x in cols
                    for x in [
                        "product",
                        "item"
                    ]
                ),

            "has_date":
                any(
                    x in cols
                    for x in [
                        "date",
                        "month",
                        "year"
                    ]
                )
        }