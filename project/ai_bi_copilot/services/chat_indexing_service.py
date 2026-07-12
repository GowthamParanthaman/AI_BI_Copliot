from __future__ import annotations

import json
from typing import Any

from langchain_core.documents import Document
from loguru import logger

from services.vector_store_service import VectorStoreService


class ChatIndexingService:
    """
    RAG Indexing Service for the AI Chat feature.

    Builds embeddings for:
    - Dataset schema
    - Column names
    - Column descriptions
    - Dataset summary
    - KPI summary
    - Business Health summary
    - Forecast summary

    Each category becomes one or more small, focused
    LangChain Documents so retrieval can return only the
    context relevant to a chat question instead of the
    whole dataset profile.
    """

    def __init__(
        self,
        vector_store_service: VectorStoreService | None = None
    ) -> None:

        self.vector_store_service = (
            vector_store_service or VectorStoreService()
        )

    # =====================================================
    # PUBLIC API
    # =====================================================

    def index_dataset(
        self,
        dataset_name: str,
        schema: dict[str, Any] | None = None,
        business_entities: dict[str, Any] | None = None,
        fact_columns: list[str] | None = None,
        dimension_columns: list[str] | None = None,
        kpi_candidates: list[str] | None = None,
        row_count: int | None = None,
        column_count: int | None = None,
        quality_score: float | None = None,
        business_domain: str | None = None,
        semantic_description: str | None = None,
        kpi_summary: dict[str, Any] | None = None,
        health_score: dict[str, Any] | None = None,
        forecast_results: dict[str, Any] | None = None,
    ) -> int:
        """
        Build and persist the RAG index for one dataset.

        Safe to call multiple times for the same dataset
        (e.g. once on upload with partial context, again
        after analysis with the full context) — previous
        embeddings for the dataset are replaced.
        """

        documents: list[Document] = []

        documents.extend(
            self._build_schema_documents(
                dataset_name=dataset_name,
                schema=schema,
                business_entities=business_entities,
                fact_columns=fact_columns,
                dimension_columns=dimension_columns,
                kpi_candidates=kpi_candidates,
            )
        )

        documents.extend(
            self._build_summary_document(
                dataset_name=dataset_name,
                row_count=row_count,
                column_count=column_count,
                quality_score=quality_score,
                business_domain=business_domain,
                semantic_description=semantic_description,
            )
        )

        documents.extend(
            self._build_kpi_document(
                dataset_name=dataset_name,
                kpi_summary=kpi_summary,
            )
        )

        documents.extend(
            self._build_health_document(
                dataset_name=dataset_name,
                health_score=health_score,
            )
        )

        documents.extend(
            self._build_forecast_document(
                dataset_name=dataset_name,
                forecast_results=forecast_results,
            )
        )

        if not documents:

            logger.warning(
                "ChatIndexingService received no indexable "
                f"content for dataset={dataset_name}"
            )

            return 0

        return self.vector_store_service.replace_dataset_documents(
            dataset_name=dataset_name,
            documents=documents,
        )

    # =====================================================
    # SCHEMA + COLUMNS + COLUMN DESCRIPTIONS
    # =====================================================

    def _build_schema_documents(
        self,
        dataset_name: str,
        schema: dict[str, Any] | None,
        business_entities: dict[str, Any] | None,
        fact_columns: list[str] | None,
        dimension_columns: list[str] | None,
        kpi_candidates: list[str] | None,
    ) -> list[Document]:

        if not schema:
            return []

        fact_columns = fact_columns or []
        dimension_columns = dimension_columns or []
        kpi_candidates = kpi_candidates or []
        business_entities = business_entities or {}

        entity_by_column: dict[str, list[str]] = {}

        for entity, columns in business_entities.items():

            for column in (columns or []):

                entity_by_column.setdefault(
                    column, []
                ).append(entity)

        documents: list[Document] = []

        column_lines = []

        for column_name, column_info in schema.items():

            role_tags = []

            if column_name in fact_columns:
                role_tags.append("fact/measure")

            if column_name in dimension_columns:
                role_tags.append("dimension")

            if column_name in kpi_candidates:
                role_tags.append("KPI candidate")

            for entity in entity_by_column.get(column_name, []):
                role_tags.append(f"business entity: {entity}")

            if isinstance(column_info, dict):

                dtype = column_info.get("dtype", "unknown")

                extra = ", ".join(
                    f"{key}={value}"
                    for key, value in column_info.items()
                    if key != "dtype"
                )

            else:

                dtype = str(column_info)
                extra = ""

            description = (
                f"Column '{column_name}' (type: {dtype}). "
                + (f"Stats: {extra}. " if extra else "")
                + (
                    f"Role: {', '.join(role_tags)}."
                    if role_tags
                    else "Role: general attribute."
                )
            )

            column_lines.append(description)

            documents.append(
                Document(
                    page_content=description,
                    metadata={
                        "dataset_name": dataset_name,
                        "category": "column",
                        "column_name": column_name,
                    }
                )
            )

        # One consolidated schema overview document, useful
        # for "what columns does this dataset have" style
        # questions without retrieving every column chunk.
        schema_overview = (
            f"Dataset '{dataset_name}' schema overview. "
            f"Columns ({len(schema)}): "
            f"{', '.join(schema.keys())}. "
            + "\n".join(column_lines)
        )

        documents.append(
            Document(
                page_content=schema_overview,
                metadata={
                    "dataset_name": dataset_name,
                    "category": "schema",
                }
            )
        )

        return documents

    # =====================================================
    # DATASET SUMMARY
    # =====================================================

    def _build_summary_document(
        self,
        dataset_name: str,
        row_count: int | None,
        column_count: int | None,
        quality_score: float | None,
        business_domain: str | None,
        semantic_description: str | None,
    ) -> list[Document]:

        parts = [
            f"Dataset '{dataset_name}' summary."
        ]

        if row_count is not None:
            parts.append(f"Rows: {row_count}.")

        if column_count is not None:
            parts.append(f"Columns: {column_count}.")

        if quality_score is not None:
            parts.append(f"Data quality score: {quality_score}.")

        if business_domain:
            parts.append(f"Business domain: {business_domain}.")

        if semantic_description:
            parts.append(semantic_description)

        if len(parts) == 1:
            return []

        return [
            Document(
                page_content=" ".join(parts),
                metadata={
                    "dataset_name": dataset_name,
                    "category": "dataset_summary",
                }
            )
        ]

    # =====================================================
    # KPI SUMMARY
    # =====================================================

    def _build_kpi_document(
        self,
        dataset_name: str,
        kpi_summary: dict[str, Any] | None,
    ) -> list[Document]:

        if not kpi_summary:
            return []

        content = (
            f"Dataset '{dataset_name}' KPI summary.\n"
            f"{self._to_readable_text(kpi_summary)}"
        )

        return [
            Document(
                page_content=content,
                metadata={
                    "dataset_name": dataset_name,
                    "category": "kpi_summary",
                }
            )
        ]

    # =====================================================
    # BUSINESS HEALTH SUMMARY
    # =====================================================

    def _build_health_document(
        self,
        dataset_name: str,
        health_score: dict[str, Any] | None,
    ) -> list[Document]:

        if not health_score:
            return []

        content = (
            f"Dataset '{dataset_name}' business health summary.\n"
            f"{self._to_readable_text(health_score)}"
        )

        return [
            Document(
                page_content=content,
                metadata={
                    "dataset_name": dataset_name,
                    "category": "health_summary",
                }
            )
        ]

    # =====================================================
    # FORECAST SUMMARY
    # =====================================================

    def _build_forecast_document(
        self,
        dataset_name: str,
        forecast_results: dict[str, Any] | None,
    ) -> list[Document]:

        if not forecast_results:
            return []

        content = (
            f"Dataset '{dataset_name}' forecast summary.\n"
            f"{self._to_readable_text(forecast_results)}"
        )

        return [
            Document(
                page_content=content,
                metadata={
                    "dataset_name": dataset_name,
                    "category": "forecast_summary",
                }
            )
        ]

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _to_readable_text(payload: dict[str, Any]) -> str:

        try:

            return json.dumps(
                payload,
                indent=2,
                default=str
            )

        except Exception:

            return str(payload)
