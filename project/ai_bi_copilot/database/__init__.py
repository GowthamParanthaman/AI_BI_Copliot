"""
Database Package

Centralized exports for database layer components.

Exposes:
- SQLAlchemy Base metadata
- Database engine
- Session factory
- Database dependency injection
"""

from database.base import Base
from database.session import (
    engine,
    SessionLocal,
    get_db
)

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
]