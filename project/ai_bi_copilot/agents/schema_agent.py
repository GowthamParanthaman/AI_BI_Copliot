from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from loguru import logger

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState


class SchemaAgent(BaseAgent):
    """
    Enterprise Schema Intelligence Agent

    Responsibilities:
    - Schema profiling
    - Semantic column classification
    - Fact/Dimension detection
    - KPI candidate detection
    - Business metadata generation
    """

    agent_name = "SchemaAgent"
    agent_version = "1.0.0"

    CUSTOMER_KEYWORDS = {
        "customer",
        "client",
        "buyer",
        "consumer"
    }

    PRODUCT_KEYWORDS = {
        "product",
        "item",
        "sku",
        "category"
    }

    DATE_KEYWORDS = {
        "date",
        "year",
        "month",
        "quarter",
        "week"
    }

    REVENUE_KEYWORDS = {
        "sales",
        "revenue",
        "amount",
        "profit",
        "income"
    }

    KPI_KEYWORDS = {
        "sales",
        "revenue",
        "profit",
        "quantity",
        "margin",
        "cost"
    }

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        if "dataframe" not in state:

            raise ValueError(
                "dataframe missing from workflow state"
            )

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        logger.info(
            f"[{self.agent_name}] Starting schema analysis"
        )

        df = state.get("dataframe")

        if df is None:
            raise ValueError(
                "dataframe missing from workflow state"
            )

        schema_info = self._build_schema(df)

        business_entities = (
            self._detect_business_entities(df)
        )

        fact_columns = (
            self._detect_fact_columns(df)
        )

        dimension_columns = (
            self._detect_dimension_columns(df)
        )

        kpi_candidates = (
            self._detect_kpi_candidates(df)
        )

        semantic_description = (
            self._generate_description(
                df=df,
                entities=business_entities,
                kpis=kpi_candidates
            )
        )

        state["schema_status"] = "COMPLETED"

        state["schema_generated_at"] = (
            datetime.utcnow().isoformat()
        )

        state["schema_info"] = schema_info

        state["business_entities"] = business_entities

        state["fact_columns"] = fact_columns

        state["dimension_columns"] = dimension_columns

        state["kpi_candidates"] = kpi_candidates

        state["semantic_description"] = (
            semantic_description
        )

        logger.success(
            f"[{self.agent_name}] "
            f"Schema analysis completed"
        )

        return state

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "schema_status",

            "schema_info",

            "business_entities"
        ]

        missing = [

            field
            for field in required_fields
            if field not in state
        ]

        if missing:

            raise RuntimeError(
                f"Missing schema outputs: {missing}"
            )

    def _build_schema(
        self,
        df: pd.DataFrame
    ) -> dict[str, Any]:

        return {

            column: {
                "dtype": str(df[column].dtype),
                "nulls": int(
                    df[column].isna().sum()
                ),
                "unique": int(
                    df[column].nunique()
                )
            }

            for column in df.columns
        }

    def _detect_business_entities(
        self,
        df: pd.DataFrame
    ) -> dict[str, list[str]]:

        entities = {

            "customer": [],
            "product": [],
            "date": [],
            "revenue": []
        }

        for column in df.columns:

            column_lower = column.lower()

            if any(
                keyword in column_lower
                for keyword in self.CUSTOMER_KEYWORDS
            ):
                entities["customer"].append(column)

            if any(
                keyword in column_lower
                for keyword in self.PRODUCT_KEYWORDS
            ):
                entities["product"].append(column)

            if any(
                keyword in column_lower
                for keyword in self.DATE_KEYWORDS
            ):
                entities["date"].append(column)

            if any(
                keyword in column_lower
                for keyword in self.REVENUE_KEYWORDS
            ):
                entities["revenue"].append(column)

        return entities

    def _detect_fact_columns(
        self,
        df: pd.DataFrame
    ) -> list[str]:

        return list(
            df.select_dtypes(
                include=["number"]
            ).columns
        )

    def _detect_dimension_columns(
        self,
        df: pd.DataFrame
    ) -> list[str]:

        return list(
            df.select_dtypes(
                exclude=["number"]
            ).columns
        )

    def _detect_kpi_candidates(
        self,
        df: pd.DataFrame
    ) -> list[str]:

        candidates = []

        for column in df.columns:

            column_lower = column.lower()

            if any(
                keyword in column_lower
                for keyword in self.KPI_KEYWORDS
            ):
                candidates.append(column)

        return candidates

    def _generate_description(
        self,
        df: pd.DataFrame,
        entities: dict[str, Any],
        kpis: list[str]
    ) -> str:

        return (
            f"Dataset contains "
            f"{len(df)} records and "
            f"{len(df.columns)} columns. "
            f"Detected business entities: "
            f"{', '.join([k for k, v in entities.items() if v])}. "
            f"KPI candidates: "
            f"{', '.join(kpis) if kpis else 'None'}."
        )