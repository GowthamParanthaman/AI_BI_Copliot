from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from loguru import logger
from sklearn.linear_model import LinearRegression


class ForecastService:

    REVENUE_KEYWORDS = [

        "revenue",
        "sales",
        "amount",
        "income",
        "total_amount",
        "total amount",
        "sales_amount"
    ]
    
    DATE_KEYWORDS = [

        "date",

        "order_date",

        "transaction_date",

        "created_at",

        "timestamp",

        "purchase_date"
    ]
    
    IGNORE_COLUMNS = {

        "unnamed: 0",

        "id",

        "index",

        "row_id",

        "record_id"
    }
    
    def _find_date_column(
        self,
        df: pd.DataFrame
    ) -> str | None:

        logger.info(
            "Searching for date column"
        )

        for column in df.columns:

            name = (
                str(column)
                .lower()
                .strip()
            )

            if name in self.IGNORE_COLUMNS:

                continue

            if any(

                keyword in name

                for keyword
                in self.DATE_KEYWORDS
            ):

                logger.success(
                    f"Date column found: {column}"
                )

                return column

        logger.warning(
            "No date column found"
        )

        return None
    
    def generate_forecast(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        logger.info(
            "Generating business forecast"
        )

        revenue_col = (
            self._find_revenue_column(
                df
            )
        )

        date_col = (
            self._find_date_column(
                df
            )
        )

        if revenue_col is None:

            return {

                "status":
                    "NO_REVENUE_COLUMN",

                "forecast_available":
                    False
            }

        if date_col is None:

            return {

                "status":
                    "NO_DATE_COLUMN",

                "forecast_available":
                    False
            }

        forecast_df = df.copy()

        forecast_df[date_col] = pd.to_datetime(
            forecast_df[date_col],
            errors="coerce"
        )

        forecast_df = forecast_df.dropna(
            subset=[date_col]
        )

        forecast_df[revenue_col] = pd.to_numeric(
            forecast_df[revenue_col],
            errors="coerce"
        ).fillna(0)

        daily_revenue = (

            forecast_df

            .groupby(date_col)[revenue_col]

            .sum()

            .reset_index()
        )

        if len(daily_revenue) < 10:

            return {

                "status":
                    "INSUFFICIENT_TIME_SERIES_DATA",

                "forecast_available":
                    False
            }

        x = np.arange(
            len(daily_revenue)
        ).reshape(-1, 1)

        y = pd.to_numeric(

            daily_revenue[
                revenue_col
            ],

            errors="coerce"

        ).fillna(0).to_numpy(
            dtype=np.float64
        )

        model = LinearRegression()

        model.fit(
            x,
            y
        )

        future_30 = np.array(
            [[float(len(y) + 30)]],
            dtype=np.float64
        )

        next_30 = float(
            model.predict(
                future_30
            )[0]
        )

        future_60 = np.array(
            [[float(len(y) + 60)]],
            dtype=np.float64
        )

        next_60 = float(
            model.predict(
                future_60
            )[0]
        )

        future_90 = np.array(
            [[float(len(y) + 90)]],
            dtype=np.float64
        )

        next_90 = float(
            model.predict(
                future_90
            )[0]
        )

        current_avg = float(
            daily_revenue[
                revenue_col
            ].mean()
        )

        growth_rate = round(

            (
                (
                    next_90
                    - current_avg
                )
                /
                max(
                    current_avg,
                    1
                )
            )
            * 100,

            2
        )

        outlook = (
            "POSITIVE"
            if growth_rate > 10
            else
            "STABLE"
            if growth_rate > 0
            else
            "NEGATIVE"
        )

        return {

            "forecast_available":
                True,

            "date_column":
                date_col,

            "revenue_column":
                revenue_col,

            "historical_periods":
                len(daily_revenue),

            "current_average":
                round(current_avg, 2),

            "next_30_days":
                round(next_30, 2),

            "next_60_days":
                round(next_60, 2),

            "next_90_days":
                round(next_90, 2),

            "growth_rate":
                growth_rate,

            "business_outlook":
                outlook,

            "confidence":
                "MEDIUM"
        }

    def _find_revenue_column(
        self,
        df: pd.DataFrame
    ) -> str | None:

        logger.info(
            f"Searching columns: {list(df.columns)}"
        )

        for column in df.columns:

            column_name = (
                str(column)
                .lower()
                .strip()
            )

            if any(
                keyword in column_name
                for keyword in self.REVENUE_KEYWORDS
            ):

                logger.success(
                    f"Revenue column found: {column}"
                )

                return column

        return None
    
    