from __future__ import annotations

from typing import Any

import pandas as pd

from loguru import logger

from services.visualization_renderer import VisualizationRenderer


class VisualizationService:
    """
    Enterprise Visualization Service

    Responsibilities
    ----------------
    - Auto chart discovery
    - KPI card generation
    - Dashboard generation
    - Trend visualization
    - Correlation analysis
    - Executive dashboard metadata

    Output
    ------
    Streamlit / Plotly compatible configs
    """

    MAX_VISUALIZATIONS = 15
    IGNORE_COLUMNS = {

        "unnamed: 0",

        "id",

        "index",

        "row_id",

        "record_id"
    }
    
    BUSINESS_PRIORITY = [

        "Total Amount",

        "Revenue",

        "Sales",

        "Profit",

        "Quantity",

        "Orders"
    ]

    # ==========================================
    # PUBLIC API
    # ==========================================

    def generate_visualizations(
        self,
        df: pd.DataFrame,
        ) -> dict[str, Any]:

        logger.info(
            "Generating enterprise visualizations"
        )

        visualizations: list[
            dict[str, Any]
        ] = []

        numeric_columns = self._numeric_columns(df)
        categorical_columns = self._categorical_columns(df)
        
        revenue_column = self._find_revenue_column(
            numeric_columns
        )

        logger.info(
            f"Revenue Column: {revenue_column}"
        )
        

        visualizations.extend(
            self.generate_kpi_cards(
                df,
                numeric_columns
            )
        )

        visualizations.extend(
            self.generate_trend_charts(
                numeric_columns
            )
        )

        visualizations.extend(
            self.generate_distribution_charts(
                numeric_columns
            )
        )

        visualizations.extend(
            self.generate_category_charts(
                numeric_columns,
                categorical_columns
            )
        )

        visualizations.extend(
            self.generate_correlation_charts(
                numeric_columns
            )
        )

        logger.success(
            f"{len(visualizations)} "
            f"visualizations generated"
        )

        visualizations = visualizations[: self.MAX_VISUALIZATIONS]

        renderer = VisualizationRenderer()

        chart_paths: list[str] = []

        chart_metadata: list[dict[str, Any]] = []

        for chart in visualizations:

            try:

                path = None

                if chart["visual_type"] == "bar_chart":

                    path = renderer.render_bar_chart(
                        df,
                        chart["x"],
                        chart["y"],
                        chart["title"],
                    )

                elif chart["visual_type"] == "line_chart":

                    metric = chart["metric"]

                    x_column = str(df.columns[0])

                    path = renderer.render_line_chart(
                        df,
                        x_column,
                        metric,
                        chart["title"],
                    )

                elif chart["visual_type"] == "histogram":

                    path = renderer.render_histogram(
                        df,
                        chart["metric"],
                        chart["title"],
                    )

                elif chart["visual_type"] == "correlation_heatmap":

                    path = renderer.render_heatmap(
                        df,
                        chart["title"],
                    )

                if path:

                    chart_paths.append(path)

                    chart_metadata.append(
                        {
                            "title": chart["title"],
                            "visual_type": chart["visual_type"],
                            "path": path,
                        }
                    )

            except Exception as exc:

                logger.exception(
                    f"Failed to render {chart['title']}: {exc}"
                )

        return {
            "visualizations": visualizations,
            "chart_paths": chart_paths,
            "chart_metadata": chart_metadata,
        }

    # ==========================================
    # KPI CARDS
    # ==========================================

    def generate_kpi_cards(
        self,
        df: pd.DataFrame,
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        priority_columns = sorted(

        numeric_columns,

        key=lambda col: (

            next(

                (
                    i

                    for i, keyword

                    in enumerate(
                        self.BUSINESS_PRIORITY
                    )

                    if keyword.lower()

                    in str(col).lower()
                ),

                999
            )
        )
    )
        priority_columns = [

            col

            for col in priority_columns

            if str(col).lower()

            not in {

                "age"
            }
        ]
        
        for column in priority_columns[:5]:
            charts.append({

                "visual_type":
                    "kpi_card",

                "title":
                    column,

                "metric":
                    column,

                "value":
                    round(

                        float(
                            df[column].sum()
                        ),

                        2
                    ),

                "average":
                    round(

                        float(
                            df[column].mean()
                        ),

                        2
                    ),

                "max":
                    round(

                        float(
                            df[column].max()
                        ),

                        2
                    ),

                "priority":
                    "HIGH"
            })

        return charts

    # ==========================================
    # TREND CHARTS
    # ==========================================

    def generate_trend_charts(
        self,
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        priority_columns = sorted(

            numeric_columns,

            key=lambda col: (

                next(

                    (
                        i

                        for i, keyword

                        in enumerate(
                            self.BUSINESS_PRIORITY
                        )

                        if keyword.lower()

                        in str(col).lower()
                    ),

                    999
                )
            )
        )

        filtered_columns = [

            col

            for col

            in priority_columns

            if str(col).lower() not in {
                "age"
            }
        ]

        for column in filtered_columns[:3]:

            charts.append({

                "visual_type":
                    "line_chart",

                "title":
                    f"{column} Trend",

                "metric":
                    column,

                "priority":
                    "HIGH"
            })

        return charts
    # ==========================================
    # DISTRIBUTION CHARTS
    # ==========================================

    def generate_distribution_charts(
        self,
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        priority_columns = sorted(

            numeric_columns,

            key=lambda col: (

                next(

                    (
                        i

                        for i, keyword

                        in enumerate(
                            self.BUSINESS_PRIORITY
                        )

                        if keyword.lower()

                        in str(col).lower()
                    ),

                    999
                )
            )
        )

        filtered_columns = [

            col

            for col
            in numeric_columns

            if str(col).lower()

            not in {

                "age"
            }
        ]

        for column in filtered_columns[:3]:

            charts.append({

                "visual_type":
                    "histogram",

                "title":
                    f"{column} Distribution",

                "metric":
                    column,

                "priority":
                    "MEDIUM"
            })

        return charts
    # ==========================================
    # CATEGORY CHARTS
    # ==========================================

    def generate_category_charts(
        self,
        numeric_columns: list[str],
        categorical_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        revenue_column = (
            self._find_revenue_column(
                numeric_columns
            )
        )

        if not revenue_column:

            return charts

        for category in categorical_columns[:3]:

            charts.append({

                "visual_type":
                    "bar_chart",

                "title":
                    f"{revenue_column} by {category}",

                "x":
                    category,

                "y":
                    revenue_column,

                "priority":
                    "HIGH"
            })

        return charts

    # ==========================================
    # CORRELATION
    # ==========================================

    def generate_correlation_charts(
        self,
        numeric_columns: list[str]
    ) -> list[dict[str, Any]]:

        charts = []

        if len(numeric_columns) < 2:

            return charts

        revenue_column = self._find_revenue_column(
            numeric_columns
        )

        quantity_column = next(

            (
                column

                for column

                in numeric_columns

                if "quantity" in column.lower()
            ),

            None
        )

        # Correlation Heatmap
        charts.append({

            "visual_type":
                "correlation_heatmap",

            "columns":
                numeric_columns,

            "title":
                "Correlation Matrix",

            "priority":
                "HIGH"
        })

        # Scatter Plot
        if revenue_column and quantity_column:

            charts.append({

                "visual_type":
                    "scatter_plot",

                "title":
                    f"{revenue_column} vs {quantity_column}",

                "x":
                    quantity_column,

                "y":
                    revenue_column,

                "priority":
                    "MEDIUM"
            })

        return charts

    # ==========================================
    # HELPERS
    # ==========================================

    @classmethod
    def _numeric_columns(
        cls,
        df: pd.DataFrame
    ) -> list[str]:

        columns = list(

            df.select_dtypes(
                include=["number"]
            ).columns
        )

        return [

            col

            for col in columns

            if str(col).lower().strip()

            not in cls.IGNORE_COLUMNS
        ]

    @classmethod
    def _categorical_columns(
        cls,
        df: pd.DataFrame
    ) -> list[str]:

        columns = list(

            df.select_dtypes(
                include=[
                    "object",
                    "category"
                ]
            ).columns
        )

        return [

            col

            for col in columns

            if str(col).lower().strip()

            not in cls.IGNORE_COLUMNS
        ]
        
    @staticmethod
    def _find_revenue_column(
        numeric_columns: list[str]
    ) -> str | None:

        revenue_keywords = [

            "revenue",
            "sales",
            "amount",
            "income",
            "profit",
            "total"
        ]

        for column in numeric_columns:

            if any(

                keyword in
                str(column).lower()

                for keyword
                in revenue_keywords
            ):

                return column

        return None    