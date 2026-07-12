from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from loguru import logger

from api.dependencies.services import get_chat_service

from api.schemas.chat import (
    ChatIndexStatusResponse,
    ChatQueryRequest,
    ChatQueryResponse,
)

from services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"]
)


@router.post(
    "/query",
    response_model=ChatQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the AI Chat a retrieval-augmented question",
    description="""
    Retrieval-Augmented Generation (RAG) endpoint for the
    AI Chat feature.

    The question is embedded and matched against the
    dataset's indexed schema, column names/descriptions,
    dataset summary, KPI summary, Business Health summary,
    and forecast summary stored in ChromaDB. Only the
    retrieved context is passed to the LLM — the chat
    never answers without retrieval.
    """
)
async def query_chat(
    request: ChatQueryRequest,
    chat_service: ChatService = Depends(
        get_chat_service
    ),
) -> ChatQueryResponse:

    try:

        result = chat_service.ask(
            question=request.question,
            dataset_name=request.dataset_name,
        )

        return ChatQueryResponse(**result)

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:

        logger.exception(
            "AI Chat query failed"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/index/status",
    response_model=ChatIndexStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check whether the AI Chat index exists",
)
async def get_index_status(
    dataset_name: str | None = None,
    chat_service: ChatService = Depends(
        get_chat_service
    ),
) -> ChatIndexStatusResponse:

    indexed = chat_service.vector_store_service.has_index(
        dataset_name
    )

    return ChatIndexStatusResponse(
        dataset_name=dataset_name,
        indexed=indexed,
    )
