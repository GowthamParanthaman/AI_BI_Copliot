from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_chroma import Chroma

from loguru import logger

from core.config import settings
from llm.provider import LLMProvider


class VectorStoreService:
    """
    RAG Vector Store Service (ChromaDB)

    Responsibilities
    ----------------
    - Persist embeddings for the AI Chat feature
    - Upsert / delete per-dataset document chunks
    - Similarity search restricted to a dataset namespace

    Storage
    -------
    Persisted on disk inside the project storage
    directory (STORAGE) so the index survives restarts,
    exactly like uploaded datasets.
    """

    COLLECTION_NAME = "ai_bi_chat_index"

    PERSIST_DIR = Path(
        settings.CHAT_VECTOR_STORE_DIR
    )

    def __init__(self) -> None:

        self.PERSIST_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        self._store: Chroma | None = None

        logger.info(
            "VectorStoreService initialized | "
            f"persist_dir={self.PERSIST_DIR}"
        )

    # =====================================================
    # LAZY STORE ACCESS
    # =====================================================

    @property
    def store(self) -> Chroma:

        if self._store is None:

            self._store = Chroma(
                collection_name=self.COLLECTION_NAME,
                embedding_function=LLMProvider.get_embeddings(),
                persist_directory=str(self.PERSIST_DIR),
            )

        return self._store

    # =====================================================
    # UPSERT
    # =====================================================

    def replace_dataset_documents(
        self,
        dataset_name: str,
        documents: list[Document]
    ) -> int:
        """
        Replace all indexed chunks for a dataset with a
        fresh set (delete-then-add) so re-analysis never
        leaves stale or duplicate embeddings behind.
        """

        self.delete_dataset(dataset_name)

        if not documents:

            logger.warning(
                "No documents supplied for indexing | "
                f"dataset={dataset_name}"
            )

            return 0

        ids = [
            f"{dataset_name}::{index}"
            for index in range(len(documents))
        ]

        self.store.add_documents(
            documents=documents,
            ids=ids
        )

        logger.success(
            f"Indexed {len(documents)} chunk(s) "
            f"for dataset={dataset_name}"
        )

        return len(documents)

    # =====================================================
    # DELETE
    # =====================================================

    def delete_dataset(
        self,
        dataset_name: str
    ) -> None:

        try:

            self.store.delete(
                where={"dataset_name": dataset_name}
            )

        except Exception as exc:

            logger.debug(
                f"No prior index to delete for "
                f"dataset={dataset_name} ({exc})"
            )

    # =====================================================
    # RETRIEVAL
    # =====================================================

    def has_index(
        self,
        dataset_name: str | None = None
    ) -> bool:

        try:

            if dataset_name:

                results = self.store.get(
                    where={"dataset_name": dataset_name},
                    limit=1
                )

            else:

                results = self.store.get(limit=1)

            return bool(
                results.get("ids")
            )

        except Exception as exc:

            logger.warning(
                f"Index existence check failed: {exc}"
            )

            return False

    def similarity_search(
        self,
        query: str,
        dataset_name: str | None = None,
        top_k: int | None = None
    ) -> list[Document]:

        k = top_k or settings.CHAT_RETRIEVAL_TOP_K

        filter_ = (
            {"dataset_name": dataset_name}
            if dataset_name
            else None
        )

        try:

            return self.store.similarity_search(
                query=query,
                k=k,
                filter=filter_
            )

        except Exception as exc:

            logger.exception(
                f"Similarity search failed: {exc}"
            )

            return []
