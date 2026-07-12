from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ChatQueryRequest(BaseModel):
    """
    AI Chat Query Request

    Retrieval-Augmented Generation (RAG) request for the
    AI Chat feature. The dataset must already be uploaded
    and indexed (embeddings built) before it can be
    queried.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    dataset_name: str | None = Field(
        default=None,
        max_length=255,
        description=(
            "Restrict retrieval to a specific indexed "
            "dataset. If omitted, retrieval searches "
            "across all indexed datasets."
        ),
        examples=["sales_2025"]
    )

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's business question"
    )


class ChatSource(BaseModel):
    """
    A single retrieved context chunk used to answer
    the chat question.
    """

    category: str = Field(...)

    column_name: str | None = Field(default=None)

    snippet: str = Field(...)


class ChatQueryResponse(BaseModel):
    """
    AI Chat Query Response
    """

    success: bool = Field(...)

    answered: bool = Field(
        ...,
        description=(
            "False when no retrieval context was found "
            "and the LLM was never called."
        )
    )

    dataset_name: str | None = Field(default=None)

    answer: str = Field(...)

    sources: list[ChatSource] = Field(default_factory=list)

    retrieved_chunks: int = Field(default=0)

    generated_at: datetime = Field(...)


class ChatIndexStatusResponse(BaseModel):
    """
    Reports whether a dataset (or the store as a whole)
    currently has an AI Chat retrieval index.
    """

    dataset_name: str | None = Field(default=None)

    indexed: bool = Field(...)
