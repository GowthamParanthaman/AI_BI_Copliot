from __future__ import annotations

from datetime import datetime
from typing import Any

from langchain_core.documents import Document
from loguru import logger

from llm.prompts import PromptRegistry
from llm.provider import LLMProvider
from services.vector_store_service import VectorStoreService

NO_INDEX_MESSAGE = (
    "I don't have any indexed dataset to answer from yet. "
    "Please upload a dataset and run analysis first — the "
    "AI Chat can only answer using retrieved context from "
    "an indexed dataset."
)

NO_CONTEXT_MESSAGE = (
    "I couldn't find any relevant indexed context for that "
    "question. Try rephrasing, or make sure the dataset you "
    "mean has been uploaded and analyzed."
)


class ChatService:
    """
    Retrieval-Augmented Generation (RAG) Chat Service.

    Extends the AI Chat feature (previously answered
    directly by ChatAgent with no retrieval) so every
    answer is grounded in embeddings retrieved from
    ChromaDB — dataset schema, column names/descriptions,
    dataset summary, KPI summary, Business Health summary,
    and forecast summary.

    Hard rule: the LLM is never invoked without retrieved
    context. If nothing relevant is indexed, a clear
    message is returned instead of a generated answer.
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

    def ask(
        self,
        question: str,
        dataset_name: str | None = None,
    ) -> dict[str, Any]:

        question = (question or "").strip()

        if not question:

            raise ValueError(
                "question is required"
            )

        if not self.vector_store_service.has_index(dataset_name):

            logger.info(
                "AI Chat query rejected — no index found | "
                f"dataset={dataset_name or 'ANY'}"
            )

            return self._response(
                answered=False,
                dataset_name=dataset_name,
                answer=NO_INDEX_MESSAGE,
                sources=[],
            )

        retrieved_docs = (
            self.vector_store_service.similarity_search(
                query=question,
                dataset_name=dataset_name,
            )
        )

        if not retrieved_docs:

            logger.info(
                "AI Chat query returned no relevant chunks | "
                f"dataset={dataset_name or 'ANY'}"
            )

            return self._response(
                answered=False,
                dataset_name=dataset_name,
                answer=NO_CONTEXT_MESSAGE,
                sources=[],
            )

        context = self._build_context(retrieved_docs)

        answer = self._generate_answer(
            context=context,
            question=question,
        )

        return self._response(
            answered=True,
            dataset_name=dataset_name,
            answer=answer,
            sources=retrieved_docs,
        )

    # =====================================================
    # LLM GENERATION — RETRIEVED CONTEXT ONLY
    # =====================================================

    def _generate_answer(
        self,
        context: str,
        question: str,
    ) -> str:

        prompt = (
            PromptRegistry.DATASET_CHAT.template.format(
                context=context,
                question=question,
            )
        )

        llm = LLMProvider.get_model()

        response = llm.invoke(prompt)

        return str(response.content).strip()

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _build_context(documents: list[Document]) -> str:

        sections = []

        for document in documents:

            category = document.metadata.get(
                "category", "context"
            )

            column_name = document.metadata.get(
                "column_name"
            )

            header = (
                f"[{category}"
                f"{f' - {column_name}' if column_name else ''}]"
            )

            sections.append(
                f"{header}\n{document.page_content}"
            )

        return "\n\n".join(sections)

    @staticmethod
    def _response(
        answered: bool,
        dataset_name: str | None,
        answer: str,
        sources: list[Document],
    ) -> dict[str, Any]:

        return {

            "success": True,

            "answered": answered,

            "dataset_name": dataset_name,

            "answer": answer,

            "sources": [
                {
                    "category": document.metadata.get(
                        "category", "context"
                    ),
                    "column_name": document.metadata.get(
                        "column_name"
                    ),
                    "snippet": document.page_content[:280],
                }
                for document in sources
            ],

            "retrieved_chunks": len(sources),

            "generated_at": datetime.utcnow(),
        }
