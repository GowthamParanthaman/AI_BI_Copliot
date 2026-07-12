"""
Service Dependencies

Purpose:
    Centralized service dependency injection.

Used By:
    - FastAPI Routes
    - Background Tasks
    - Agent Workflows
    - Scheduled Jobs

Benefits:
    - Loose coupling
    - Testability
    - Dependency overrides
    - Clean architecture
"""

from typing import Annotated

from fastapi import Depends

from sqlalchemy.orm import Session

from api.dependencies.database import (
    get_db
)

from services.dataset_service import (
    DatasetService
)
from functools import lru_cache

from services.bi_service import BIService
from services.chat_service import ChatService

# =====================================================
# DATABASE DEPENDENCY TYPE
# =====================================================

DatabaseSession = Annotated[
    Session,
    Depends(get_db)
]


# =====================================================
# DATASET SERVICE
# =====================================================

def get_dataset_service(
    db: DatabaseSession
) -> DatasetService:
    """
    Dataset Service Dependency

    Returns:
        DatasetService
    """

    return DatasetService(
        db=db
    )


# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    "DatabaseSession",
    "get_dataset_service"
]

@lru_cache(maxsize=1)
def get_bi_service() -> BIService:
    """
    BI Service Dependency
    """

    return BIService()
@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    """
    Chat Service Dependency (RAG-backed AI Chat)
    """

    return ChatService()


__all__ = [
    "DatabaseSession",
    "get_dataset_service",
    "get_bi_service",
    "get_chat_service"
]
