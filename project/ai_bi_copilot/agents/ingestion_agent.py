from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from loguru import logger

from agents.base_agent import BaseAgent
from workflows.state import BIWorkflowState


class IngestionAgent(BaseAgent):
    """
    Enterprise Data Ingestion Agent

    Responsibilities:
    - File validation
    - Dataset loading
    - Metadata extraction
    - Schema extraction
    - Data profiling
    - Workflow state initialization
    """

    agent_name = "IngestionAgent"
    agent_version = "1.0.0"

    SUPPORTED_FILE_TYPES = {
        ".csv",
        ".xlsx",
        ".xls",
        ".json",
        ".parquet"
    }

    def validate_input(
        self,
        state: BIWorkflowState
    ) -> None:

        file_path = state.get("file_path")

        if not file_path:
            raise ValueError(
                "file_path is required"
            )

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_FILE_TYPES:
            raise ValueError(
                f"Unsupported file type: {path.suffix}"
            )

    def execute(
        self,
        state: BIWorkflowState
    ) -> BIWorkflowState:

        file_path = state.get("file_path")

        if not file_path:
            raise ValueError(
                "file_path missing from workflow state"
            )

        path = Path(file_path)

        logger.info(
            f"[{self.agent_name}] "
            f"Loading dataset: {path.name}"
        )

        df = self._load_dataframe(path)

        self._populate_metadata(
            state=state,
            dataframe=df,
            path=path
        )

        logger.success(
            f"[{self.agent_name}] "
            f"Rows={state.get('row_count', 0)} "
            f"Columns={state.get('column_count', 0)}"
        )

        return state

    # ==================================================
    # FILE LOADER
    # ==================================================

    def _load_dataframe(
        self,
        path: Path
    ) -> pd.DataFrame:

        suffix = path.suffix.lower()

        if suffix == ".csv":

            return pd.read_csv(
                path,
                low_memory=False
            )

        if suffix in [".xlsx", ".xls"]:

            return pd.read_excel(path)

        if suffix == ".json":

            return pd.read_json(path)

        if suffix == ".parquet":

            return pd.read_parquet(path)

        raise ValueError(
            f"Unsupported format: {suffix}"
        )

    # ==================================================
    # METADATA EXTRACTION
    # ==================================================

    def _populate_metadata(
        self,
        state: BIWorkflowState,
        dataframe: pd.DataFrame,
        path: Path
    ) -> None:

        row_count = len(dataframe)
        column_count = len(dataframe.columns)

        missing_values = int(
            dataframe.isna().sum().sum()
        )

        duplicate_rows = int(
            dataframe.duplicated().sum()
        )

        memory_usage_mb = round(
            dataframe.memory_usage(
                deep=True
            ).sum() / 1024 / 1024,
            2
        )

        schema: dict[str, Any] = {
            str(column): str(dtype)
            for column, dtype
            in dataframe.dtypes.items()
        }

        state["dataframe"] = dataframe

        state["file_name"] = path.name
        state["file_extension"] = path.suffix
        state["file_path"] = str(path)

        state["file_size_mb"] = round(
            path.stat().st_size / 1024 / 1024,
            2
        )

        state["row_count"] = row_count
        state["column_count"] = column_count

        state["missing_values_count"] = missing_values
        state["duplicate_rows_count"] = duplicate_rows

        state["memory_usage_mb"] = memory_usage_mb

        state["columns"] = [
            str(col)
            for col in dataframe.columns
        ]

        state["schema"] = schema

        state["ingested_at"] = (
            datetime.utcnow().isoformat()
        )

        state["ingestion_status"] = "COMPLETED"
    # ==================================================
    # OUTPUT VALIDATION
    # ==================================================

    def validate_output(
        self,
        state: BIWorkflowState
    ) -> None:

        required_fields = [

            "dataframe",
            "row_count",
            "column_count",
            "schema",
            "columns",
            "ingestion_status"
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