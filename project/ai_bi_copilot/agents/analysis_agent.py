from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import numpy as np

from loguru import logger

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState


class AnalysisAgent(BaseAgent):
    """
    Enterprise Business Analysis Agent

    Responsibilities
    ----------------
    - Dataset profiling
    - Statistical analysis
    - Correlation analysis
    - Distribution analysis
    - Outlier analysis
    - Top/Bottom performers
    - Business insight generation
    """

    agent_name = "AnalysisAgent"
    agent_version = "2.0.0"

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:
        
        logger.info(
            f"[{self.agent_name}] Starting analysis"
        )

        self.validate_input(state)

        dataframe = state.get(
            "dataframe"
        )

        if dataframe is None:
            raise ValueError(
                "dataframe missing from workflow state"
            )

        assert isinstance(dataframe, pd.DataFrame)

        df = dataframe

        dataset_profile = self._dataset_profile(df)

        numerical_summary = self._numerical_summary(df)

        correlation_analysis = self._correlation_analysis(df)

        distribution_analysis = self._distribution_analysis(df)

        outlier_analysis = self._outlier_analysis(df)

        top_performers = self._top_performers(df)

        business_insights = self._generate_business_insights(
            df=df,
            profile=dataset_profile
        )

        state["analysis_status"] = "COMPLETED"

        state["analysis_completed_at"] = (
            datetime.utcnow().isoformat()
        )

        state["dataset_profile"] = dataset_profile

        state["numerical_summary"] = numerical_summary

        state["correlation_analysis"] = correlation_analysis

        state["distribution_analysis"] = distribution_analysis

        state["outlier_analysis"] = outlier_analysis

        state["top_performers"] = top_performers

        state["business_insights"] = business_insights
        
        state["analysis_results"] = {

            "dataset_profile":
                dataset_profile,

            "descriptive_statistics":
                numerical_summary,

            "correlations":
                correlation_analysis,

            "distribution_analysis":
                distribution_analysis,

            "outlier_analysis":
                outlier_analysis,

            "top_performers":
                top_performers,

            "business_insights":
                business_insights
        }

        self.validate_output(state)

        logger.success(
            f"[{self.agent_name}] Analysis completed"
        )

        return state

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

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
                "dataframe must be pandas DataFrame"
            )

    # =====================================================
    # OUTPUT VALIDATION
    # =====================================================

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "analysis_status",

            "dataset_profile",

            "business_insights",

            "analysis_results"
        ]

        missing = [

            field
            for field in required_fields
            if field not in state
        ]

        if missing:

            raise RuntimeError(
                f"Missing analysis outputs: {missing}"
            )

    # =====================================================
    # DATASET PROFILE
    # =====================================================

    def _dataset_profile(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        return {

            "rows":
                int(len(df)),

            "columns":
                int(len(df.columns)),

            "memory_usage_mb":
                round(
                    df.memory_usage(
                        deep=True
                    ).sum()
                    / 1024
                    / 1024,
                    2
                ),

            "numeric_columns":
                len(
                    df.select_dtypes(
                        include=["number"]
                    ).columns
                ),

            "categorical_columns":
                len(
                    df.select_dtypes(
                        exclude=["number"]
                    ).columns
                )
        }

    # =====================================================
    # CORRELATION ANALYSIS
    # =====================================================

    def _correlation_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        if len(numeric_df.columns) < 2:
            return {}

        corr_matrix = (
            numeric_df
            .corr(
                numeric_only=True
            )
            .round(4)
        )

        strong_correlations = []

        for col1 in corr_matrix.columns:

            for col2 in corr_matrix.columns:

                if col1 >= col2:
                    continue

                value = float(
                    corr_matrix[col1][col2]
                )

                if value >= 0.70:

                    strong_correlations.append({

                        "column_1":
                            col1,

                        "column_2":
                            col2,

                        "correlation":
                            round(
                                value,
                                4
                            )
                    })

        return {

            "correlation_matrix":
                corr_matrix
                .to_dict(),

            "strong_correlations":
                strong_correlations,

            "strong_correlation_count":
                len(
                    strong_correlations
                )
        }

        
    # =====================================================
    # DISTRIBUTION ANALYSIS
    # =====================================================

    def _distribution_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        if numeric_df.empty:
            return {}

        result = {}

        for column in numeric_df.columns:

            series = (
                numeric_df[column]
                .dropna()
            )

            skewness = float(
                np.asarray(
                    series.skew()
                ).item()
            )

            kurtosis = float(
                np.asarray(
                    series.kurt()
                ).item()
            )

            if abs(skewness) < 0.5:

                distribution = "NORMAL"

            elif skewness > 0.5:

                distribution = "RIGHT_SKEWED"

            else:

                distribution = "LEFT_SKEWED"

            result[column] = {

                "skewness":
                    round(
                        skewness,
                        4
                    ),

                "kurtosis":
                    round(
                        kurtosis,
                        4
                    ),

                "distribution":
                    distribution
            }

        return result
    # =====================================================
    # OUTLIER ANALYSIS
    # =====================================================

    def _outlier_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        result = {}

        for column in numeric_df.columns:

            series = (
                numeric_df[column]
                .dropna()
            )

            if len(series) < 5:
                continue

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

            outliers = series[
                (series < lower_bound)
                |
                (series > upper_bound)
            ]

            outlier_count = len(
                outliers
            )

            outlier_percentage = round(
                (
                    outlier_count
                    /
                    max(
                        len(series),
                        1
                    )
                ) * 100,
                2
            )

            result[column] = {

                "outlier_count":
                    int(
                        outlier_count
                    ),

                "outlier_percentage":
                    outlier_percentage,

                "lower_bound":
                    round(
                        float(
                            lower_bound
                        ),
                        2
                    ),

                "upper_bound":
                    round(
                        float(
                            upper_bound
                        ),
                        2
                    ),

                "risk_level":
                    (
                        "HIGH"
                        if outlier_percentage > 10
                        else "MEDIUM"
                        if outlier_percentage > 5
                        else "LOW"
                    )
            }

        return result

    # =====================================================
    # TOP PERFORMERS
    # =====================================================

    def _top_performers(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        results: dict[str, Any] = {}

        numeric_columns = list(
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        if not numeric_columns:
            return results

        for column in numeric_columns:

            series = (
                df[column]
                .dropna()
            )

            if series.empty:
                continue

            results[column] = {

                "highest_value":
                    round(
                        float(series.max()),
                        2
                    ),

                "lowest_value":
                    round(
                        float(series.min()),
                        2
                    ),

                "average_value":
                    round(
                        float(series.mean()),
                        2
                    ),

                "median_value":
                    round(
                        float(series.median()),
                        2
                    ),

                "standard_deviation":
                    round(
                        float(series.std()),
                        2
                    ),

                "variance":
                    round(
                        float(series.var()),
                        2
                    ),

                "percentile_25":
                    round(
                        float(series.quantile(0.25)),
                        2
                    ),

                "percentile_75":
                    round(
                        float(series.quantile(0.75)),
                        2
                    ),

                "percentile_95":
                    round(
                        float(series.quantile(0.95)),
                        2
                    ),

                "top_5_values":
                    [
                        round(float(x), 2)
                        for x in series.nlargest(5)
                    ],

                "bottom_5_values":
                    [
                        round(float(x), 2)
                        for x in series.nsmallest(5)
                    ]
            }

        return results
    
    # =====================================================
    # REVENUE ANALYSIS
    # =====================================================

    def _revenue_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        revenue_keywords = [

            "revenue",
            "sales",
            "amount",
            "income",
            "total"
        ]

        revenue_column = None

        for column in df.columns:

            name = str(column).lower()

            if any(
                keyword in name
                for keyword in revenue_keywords
            ):
                revenue_column = column
                break

        if revenue_column is None:
            return {}

        revenue = (
            df[revenue_column]
            .fillna(0)
        )

        return {

            "revenue_column":
                revenue_column,

            "total_revenue":
                round(
                    float(revenue.sum()),
                    2
                ),

            "average_revenue":
                round(
                    float(revenue.mean()),
                    2
                ),

            "maximum_transaction":
                round(
                    float(revenue.max()),
                    2
                ),

            "minimum_transaction":
                round(
                    float(revenue.min()),
                    2
                )
        }
        
    # =====================================================
    # CUSTOMER ANALYSIS
    # =====================================================

    def _customer_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        customer_keywords = [

            "customer",
            "client",
            "buyer"
        ]

        customer_column = None

        for column in df.columns:

            name = str(column).lower()

            if any(
                keyword in name
                for keyword in customer_keywords
            ):
                customer_column = column
                break

        if customer_column is None:
            return {}

        unique_customers = (
            df[customer_column]
            .nunique()
        )

        total_records = len(df)

        repeat_rate = round(

            (
                (
                    total_records
                    - unique_customers
                )
                /
                max(unique_customers, 1)
            ) * 100,

            2
        )

        return {

            "customer_column":
                customer_column,

            "unique_customers":
                int(unique_customers),

            "repeat_customer_rate":
                repeat_rate
        }    
    # =====================================================
    # TIME ANALYSIS
    # =====================================================

    def _time_analysis(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        date_column = None

        for column in df.columns:

            if "date" in str(column).lower():

                date_column = column
                break

        if date_column is None:
            return {}

        date_series = pd.to_datetime(
            df[date_column],
            errors="coerce"
        )

        return {

            "date_column":
                date_column,

            "start_date":
                str(date_series.min()),

            "end_date":
                str(date_series.max()),

            "analysis_period_days":
                int(
                    (
                        date_series.max()
                        -
                        date_series.min()
                    ).days
                )
        }
    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    def _executive_summary(
        self,
        profile: dict[str, Any],
        revenue: dict[str, Any]
    ) -> list[str]:

        summary = []

        summary.append(
            f"Dataset contains {profile['rows']} records."
        )

        summary.append(
            f"Dataset contains {profile['columns']} columns."
        )

        if revenue:

            summary.append(
                f"Total revenue is "
                f"{revenue['total_revenue']:,.2f}"
            )

        return summary    
    # =====================================================
    # BUSINESS INSIGHTS
    # =====================================================

    def _generate_business_insights(
        self,
        df: pd.DataFrame,
        profile: dict[str, Any]
    ) -> list[str]:

        insights: list[str] = []

        # ==========================================
        # DATASET OVERVIEW
        # ==========================================

        insights.append(
            f"Dataset contains "
            f"{profile['rows']:,} records "
            f"across "
            f"{profile['columns']} columns."
        )

        insights.append(
            f"Detected "
            f"{profile['numeric_columns']} numeric "
            f"and "
            f"{profile['categorical_columns']} "
            f"categorical attributes."
        )

        # ==========================================
        # NUMERIC COLUMN INSIGHTS
        # ==========================================

        numeric_columns = list(
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numeric_columns[:5]:

            series = (
                df[column]
                .dropna()
            )

            if series.empty:
                continue

            mean_value = round(
                float(series.mean()),
                2
            )

            max_value = round(
                float(series.max()),
                2
            )

            min_value = round(
                float(series.min()),
                2
            )

            insights.append(
                f"{column} averages "
                f"{mean_value:,} "
                f"with a range from "
                f"{min_value:,} "
                f"to "
                f"{max_value:,}."
            )

        # ==========================================
        # MISSING DATA
        # ==========================================

        missing_values = int(
            df.isna()
            .sum()
            .sum()
        )

        if missing_values == 0:

            insights.append(
                "No missing values detected. "
                "Dataset quality is excellent."
            )

        else:

            insights.append(
                f"{missing_values:,} missing values "
                f"detected across the dataset."
            )

        # ==========================================
        # DUPLICATES
        # ==========================================

        duplicate_rows = int(
            df.duplicated()
            .sum()
        )

        if duplicate_rows > 0:

            insights.append(
                f"{duplicate_rows:,} duplicate rows "
                f"identified and should be reviewed."
            )

        # ==========================================
        # TOP CATEGORIES
        # ==========================================

        categorical_columns = list(
            df.select_dtypes(
                include=["object"]
            ).columns
        )

        for column in categorical_columns[:3]:

            top_values = (
                df[column]
                .value_counts()
                .head(1)
            )

            if not top_values.empty:

                top_category = (
                    top_values.index[0]
                )

                count = int(
                    top_values.iloc[0]
                )

                insights.append(
                    f"Top {column} is "
                    f"'{top_category}' "
                    f"with {count:,} records."
                )

        # ==========================================
        # BUSINESS SIGNALS
        # ==========================================

        if len(df) > 10000:

            insights.append(
                "Large dataset detected. "
                "Suitable for advanced forecasting "
                "and trend analysis."
            )

        if len(numeric_columns) >= 5:

            insights.append(
                "Rich numerical dataset detected. "
                "Suitable for KPI modeling "
                "and predictive analytics."
            )

        # ==========================================
        # EXECUTIVE INSIGHT
        # ==========================================

        insights.append(
            "Dataset is ready for KPI generation, "
            "executive reporting, and business "
            "decision support."
        )

        return insights
    # =====================================================
    # NUMERICAL SUMMARY
    # =====================================================

    def _numerical_summary(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        numeric_df = df.select_dtypes(
            include=["number"]
        )

        if numeric_df.empty:
            return {}

        result = {}

        for column in numeric_df.columns:

            series = (
                numeric_df[column]
                .dropna()
            )

            result[column] = {

                "count":
                    int(series.count()),

                "sum":
                    round(float(series.sum()), 2),

                "mean":
                    round(float(series.mean()), 2),

                "median":
                    round(float(series.median()), 2),

                "min":
                    round(float(series.min()), 2),

                "max":
                    round(float(series.max()), 2),

                "std":
                    round(float(series.std()), 2)
            }

        return result    