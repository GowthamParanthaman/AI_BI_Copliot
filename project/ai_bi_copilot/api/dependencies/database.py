"""
Database Dependencies

Purpose:
    Centralized database dependency injection.

Used By:
    - FastAPI Routes
    - Services
    - Background Jobs
    - Agent Workflows

Example:
    @router.get("/")
    def get_items(
        db: Session = Depends(get_db)
    ):
        ...
"""

from typing import Generator

from sqlalchemy.orm import Session

from database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Database Session Dependency

    Creates a new SQLAlchemy session
    for each request and ensures
    proper cleanup.

    Yields:
        Session: SQLAlchemy session
    """

    db = SessionLocal()

    try:

        yield db

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


__all__ = [
    "get_db"
]