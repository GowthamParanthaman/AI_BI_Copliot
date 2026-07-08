from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from loguru import logger

from agents.base_agent import BaseAgent

from services.visualization_renderer import VisualizationRenderer


from workflows.state import BIWorkflowState

from datetime import UTC


class VisualizationAgent(BaseAgent):
    """
    Enterprise Visualization Agent

    Responsibilities
    ----------------
    - Visualization discovery
    - Dashboard planning
    - Chart recommendation
    - Correlation visualization detection
    - Time series detection
    - KPI visualization generation

    Output
    ------
    state["visualizations"]
    state["dashboard_layout"]
    """

    agent_name = "VisualizationAgent"

    agent_version = "2.0.0"

    MAX_CHARTS = 20
    
    renderer = VisualizationRenderer()

    def execute(
            self,
            state: BIWorkflowState
        ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting visualization planning"
        )

        self.validate_input(state)

        dataframe = state.get("dataframe")

        if dataframe is None:
            raise ValueError(
                "dataframe not found in workflow state."
            )
        df: pd.DataFrame = dataframe
        renderer = VisualizationRenderer()
    
        chart_paths: list[str] = []
        chart_metadata: list[dict[str, Any]] = []

        visualizations: list[dict[str, Any]] = []

        numeric_columns = self._get_numeric_columns(df)

        categorical_columns = (
            self._get_categorical_columns(df)
        )

        datetime_columns = (
            self._get_datetime_columns(df)
        )

        # ==========================================
        # KPI CARDS
        # ==========================================

        visualizations.extend(
            self._generate_kpi_cards(
                numeric_columns
            )
        )

        # ==========================================
        # HISTOGRAMS
        # ==========================================

        visualizations.extend(
            self._generate_histograms(
                numeric_columns
            )
        )

        # ==========================================
        # CATEGORY COMPARISONS
        # ==========================================

        visualizations.extend(
            self._generate_bar_charts(
                categorical_columns,
                numeric_columns
            )
        )

        # ==========================================
        # TIME SERIES
        # ==========================================

        visualizations.extend(
            self._generate_time_series(
                datetime_columns,
                numeric_columns
            )
        )

        # ==========================================
        # CORRELATION
        # ==========================================

        if len(numeric_columns) >= 2:

            visualizations.append({

                "priority": 1,

                "chart_type":
                    "correlation_heatmap",

                "title":
                    "Correlation Matrix",

                "columns":
                    numeric_columns
            })

        visualizations = (
            visualizations[: self.MAX_CHARTS]
        )
        
        for chart in visualizations:

            try:

                chart_type = chart.get("chart_type")

                path = None

                if chart_type == "bar":

                    path = renderer.render_bar_chart(
                        dataframe=df,
                        category=chart["x"],
                        value=chart["y"],
                        title=chart["title"],
                    )

                elif chart_type == "line":

                    path = renderer.render_line_chart(
                        dataframe=df,
                        x_column=chart["x"],
                        y_column=chart["y"],
                        title=chart["title"],
                    )

                elif chart_type == "histogram":

                    path = renderer.render_histogram(
                        dataframe=df,
                        column=chart["column"],
                        title=chart["title"],
                    )

                elif chart_type == "pie":

                    path = renderer.render_pie_chart(
                        dataframe=df,
                        category=chart["x"],
                        value=chart["y"],
                        title=chart["title"],
                    )

                elif chart_type == "correlation_heatmap":

                    path = renderer.render_heatmap(
                        dataframe=df,
                        title=chart["title"],
                    )

                if path:

                    chart_paths.append(path)

                    chart_metadata.append(
                        {
                            "title": chart["title"],
                            "chart_type": chart_type,
                            "path": path,
                        }
                    )

            except Exception as exc:

                logger.exception(
                    f"Failed to render chart {chart.get('title')}: {exc}"
                )
        
        

        dashboard_layout = {

            "overview":

                [v for v in visualizations
                if v["chart_type"] == "kpi_card"],

            "performance":

                [v for v in visualizations
                if v["chart_type"]
                in ["bar", "line"]],

            "distribution":

                [v for v in visualizations
                if v["chart_type"]
                == "histogram"],

            "advanced":

                [v for v in visualizations
                if v["chart_type"]
                == "correlation_heatmap"]
        }

        state["visualizations"] = visualizations
        
        state["chart_paths"] = chart_paths
        
        state["chart_metadata"] = chart_metadata
        
        state["visualization_count"] = len(chart_paths)

        state["dashboard_layout"] = dashboard_layout

        state["visualization_generated_at"] = (
            datetime.now(UTC).isoformat()
        )

        state["visualization_status"] = "COMPLETED"
        self.validate_output(state)

        logger.success(
            f"[{self.agent_name}] "
            f"{len(visualizations)} charts planned"
        )

        return state

    # ==================================================
    # VALIDATION
    # ==================================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        dataframe = state.get("dataframe")

        if dataframe is None:
            raise ValueError(
                "dataframe missing from workflow state"
            )

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        if not state.get("visualizations"):

            raise RuntimeError(
                "Visualization generation failed"
            )

    # ==================================================
    # COLUMN DETECTION
    # ==================================================

    @staticmethod
    def _get_numeric_columns(
        df: pd.DataFrame
    ) -> list[str]:

        return list(
            df.select_dtypes(
                include=["number"]
            ).columns
        )

    @staticmethod
    def _get_categorical_columns(
        df: pd.DataFrame
    ) -> list[str]:

        return list(
            df.select_dtypes(
                include=["object"]
            ).columns
        )

    @staticmethod
    def _get_datetime_columns(
        df: pd.DataFrame
    ) -> list[str]:

        datetime_columns = []

        for column in df.columns:

            if "date" in column.lower():

                datetime_columns.append(
                    column
                )

        return datetime_columns

    # ==================================================
    # KPI CARDS
    # ==================================================

    def _generate_kpi_cards(
        self,
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        for column in numeric_columns[:5]:

            charts.append({

                "priority": 1,

                "chart_type":
                    "kpi_card",

                "column":
                    column,

                "title":
                    column.replace(
                        "_",
                        " "
                    ).title()
            })

        return charts

    # ==================================================
    # HISTOGRAMS
    # ==================================================

    def _generate_histograms(
        self,
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        for column in numeric_columns[:5]:

            charts.append({

                "priority": 2,

                "chart_type":
                    "histogram",

                "column":
                    column,

                "title":
                    f"{column} Distribution"
            })

        return charts

    # ==================================================
    # BAR CHARTS
    # ==================================================

    def _generate_bar_charts(
        self,
        categorical_columns: list[str],
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        if not categorical_columns:

            return charts

        if not numeric_columns:

            return charts

        charts.append({

            "priority": 1,

            "chart_type":
                "bar",

            "x":
                categorical_columns[0],

            "y":
                numeric_columns[0],

            "title":
                "Category Performance"
        })

        return charts

    # ==================================================
    # TIME SERIES
    # ==================================================

    def _generate_time_series(
        self,
        datetime_columns: list[str],
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        if not datetime_columns:

            return charts

        if not numeric_columns:

            return charts

        charts.append({

            "priority": 1,

            "chart_type":
                "line",

            "x":
                datetime_columns[0],

            "y":
                numeric_columns[0],

            "title":
                "Trend Analysis"
        })

        return charts