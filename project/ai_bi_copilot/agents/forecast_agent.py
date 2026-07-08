from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from loguru import logger

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState


class ForecastAgent(BaseAgent):

    agent_name = "ForecastAgent"

    agent_version = "2.0.0"

    # ==========================================
    # INPUT VALIDATION
    # ==========================================

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        if "dataframe" not in state:

            raise ValueError(
                "dataframe missing from workflow state"
            )

    # ==========================================
    # EXECUTE
    # ==========================================

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting forecast"
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

        if not isinstance(
            df,
            pd.DataFrame
        ):

            raise TypeError(
                "dataframe must be a pandas DataFrame"
            )

        revenue_col = (
            self._find_revenue_column(
                df
            )
        )

        if revenue_col is None:

            state["forecast_results"] = {

                "message":
                    "Revenue column not found"
            }

            state["forecast_status"] = (
                "COMPLETED"
            )

            return state

        revenue_series = pd.to_numeric(
            df[revenue_col],
            errors="coerce"
        ).fillna(0)

        if len(revenue_series) < 20:

            state["forecast_results"] = {

                "message":
                    "Insufficient data for forecasting"
            }

            state["forecast_status"] = (
                "COMPLETED"
            )

            return state

        X = np.arange(
            len(revenue_series)
        ).reshape(-1, 1)

        y = revenue_series.values

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.2,
                shuffle=False
            )
        )

        models = {

            "LinearRegression":
                LinearRegression(),

            "RandomForest":
                RandomForestRegressor(
                    n_estimators=200,
                    random_state=42
                )
        }

        scores = {}

        trained_models = {}

        for name, model in models.items():

            model.fit(
                X_train,
                y_train
            )

            predictions = model.predict(
                X_test
            )

            mae = mean_absolute_error(
                y_test,
                predictions
            )

            scores[name] = mae

            trained_models[name] = model

            logger.info(
                f"{name} MAE={mae:.2f}"
            )

        best_model_name = min(
            scores.items(),
            key=lambda item: item[1]
        )[0]

        best_model = trained_models[
            best_model_name
        ]

        future_30 = float(
            best_model.predict(
                [[len(y) + 30]]
            )[0]
        )

        future_60 = float(
            best_model.predict(
                [[len(y) + 60]]
            )[0]
        )

        future_90 = float(
            best_model.predict(
                [[len(y) + 90]]
            )[0]
        )

        current_avg = float(
            revenue_series.mean()
        )

        growth_rate = round(

            (
                (
                    future_90
                    - current_avg
                )
                /
                max(
                    current_avg,
                    1
                )
            ) * 100,

            2
        )

        state["forecast_results"] = {

            "revenue_column":
                revenue_col,

            "best_model":
                best_model_name,

            "model_scores":
                {
                    k: round(v, 2)
                    for k, v
                    in scores.items()
                },

            "next_30_days":
                round(
                    future_30,
                    2
                ),

            "next_60_days":
                round(
                    future_60,
                    2
                ),

            "next_90_days":
                round(
                    future_90,
                    2
                )
        }

        state["growth_rate"] = (
            growth_rate
        )

        state[
            "forecast_horizon_days"
        ] = 90

        state[
            "forecast_generated_at"
        ] = (
            datetime.utcnow()
            .isoformat()
        )

        state[
            "forecast_status"
        ] = "COMPLETED"

        logger.success(
            f"[{self.agent_name}] "
            f"Best Model = {best_model_name}"
        )

        return state

    # ==========================================
    # REVENUE DETECTION
    # ==========================================

    def _find_revenue_column(
        self,
        df: pd.DataFrame
    ) -> str | None:

        keywords = [

            "revenue",
            "sales",
            "amount",
            "income",
            "total_amount",
            "total amount"
        ]

        for column in df.columns:

            name = (
                str(column)
                .lower()
                .strip()
            )

            if any(
                keyword in name
                for keyword in keywords
            ):

                logger.info(
                    f"Revenue column: {column}"
                )

                return column

        return None