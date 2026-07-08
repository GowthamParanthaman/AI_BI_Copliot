from __future__ import annotations

import itertools
from pathlib import Path
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import pandas as pd

from loguru import logger


class VisualizationRenderer:
    """
    Enterprise Visualization Renderer

    Responsibilities
    ----------------
    - Render charts as PNG files
    - Save charts to disk
    - Return generated image paths
    """

    OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "reports" / "charts"

    # Class-level monotonic counter: guarantees uniqueness even when
    # multiple charts are generated within the same microsecond.
    _counter = itertools.count(1)

    def __init__(self) -> None:

        self.OUTPUT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _generate_filename(
        self,
        chart_name: str,
    ) -> Path:

        # Microsecond timestamp + monotonic counter = guaranteed unique filename
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S%f")
        seq = next(self.__class__._counter)
        filename = f"{chart_name}_{timestamp}_{seq:04d}.png"

        return self.OUTPUT_DIRECTORY / filename

    def render_bar_chart(
        self,
        dataframe: pd.DataFrame,
        category: str,
        value: str,
        title: str,
    ) -> str:

        output = self._generate_filename("bar_chart")

        chart = (
            dataframe.groupby(category)[value]
            .sum()
            .sort_values(ascending=False)
        )

        plt.figure(figsize=(10, 6), dpi=300)

        chart.plot(kind="bar")

        plt.title(title)

        plt.xlabel(category)

        plt.ylabel(value)

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.savefig(
            output,
            dpi=300,
            facecolor="white"
        )

        plt.close()

        logger.success(f"Generated {output}")

        return str(output)

    def render_line_chart(
        self,
        dataframe: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
    ) -> str:

        output = self._generate_filename("line_chart")

        plt.figure(figsize=(10, 6), dpi=300)

        plt.plot(
            dataframe[x_column],
            dataframe[y_column],
            marker="o"
        )

        plt.title(title)

        plt.xlabel(x_column)

        plt.ylabel(y_column)

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.savefig(
            output,
            dpi=300,
            facecolor="white"
        )

        plt.close()

        logger.success(f"Generated {output}")

        return str(output)

    def render_histogram(
        self,
        dataframe: pd.DataFrame,
        column: str,
        title: str,
    ) -> str:

        output = self._generate_filename("histogram")

        plt.figure(figsize=(8, 6), dpi=300)

        plt.hist(
            dataframe[column].dropna(),
            bins=20
        )

        plt.title(title)

        plt.xlabel(column)

        plt.ylabel("Frequency")

        plt.tight_layout()

        plt.savefig(
            output,
            dpi=300,
            facecolor="white"
        )

        plt.close()

        logger.success(f"Generated {output}")

        return str(output)

    def render_pie_chart(
        self,
        dataframe: pd.DataFrame,
        category: str,
        value: str,
        title: str,
    ) -> str:

        output = self._generate_filename("pie_chart")

        chart = (
            dataframe.groupby(category)[value]
            .sum()
        )

        plt.figure(figsize=(8, 8), dpi=300)

        plt.pie(
            chart.astype(float).tolist(),
            labels=chart.index.tolist(),
            autopct="%1.1f%%",
        )

        plt.title(title)

        plt.tight_layout()

        plt.savefig(
            output,
            dpi=300,
            facecolor="white"
        )

        plt.close()

        logger.success(f"Generated {output}")

        return str(output)

    def render_heatmap(
        self,
        dataframe: pd.DataFrame,
        title: str,
    ) -> str:

        output = self._generate_filename("heatmap")

        correlation = dataframe.corr(numeric_only=True)

        plt.figure(figsize=(8, 6), dpi=300)

        plt.imshow(
            correlation,
            aspect="auto"
        )

        plt.xticks(
            range(len(correlation.columns)),
            correlation.columns.tolist(),
            rotation=90
        )

        plt.yticks(
            range(len(correlation.columns)),
            correlation.columns.tolist()
        )

        plt.colorbar()

        plt.title(title)

        plt.tight_layout()

        plt.savefig(
            output,
            dpi=300,
            facecolor="white"
        )

        plt.close()

        logger.success(f"Generated {output}")

        return str(output)
