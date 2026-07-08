"""
Database Initialization Module

Responsibilities:
- Validate database connectivity
- Create database schema
- Register ORM models
- Provide startup initialization
- Support application lifecycle hooks
"""

from __future__ import annotations

from typing import Final

from loguru import logger

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.base import Base
from database.session import engine

# Register all models
from database.models.dataset import Dataset


APPLICATION_NAME: Final[str] = "AI BI Copilot"


class DatabaseInitializationError(Exception):
    """
    Raised when database initialization fails.
    """
    pass


class DatabaseInitializer:
    """
    Enterprise Database Initializer.

    Handles:
    - Connection validation
    - Schema creation
    - Startup diagnostics
    """

    @staticmethod
    def validate_connection() -> bool:
        """
        Validate active database connection.
        """

        try:

            logger.info(
                "Validating database connection..."
            )

            with engine.connect() as connection:

                connection.execute(
                    text("SELECT 1")
                )

            logger.success(
                "Database connection successful"
            )

            return True

        except SQLAlchemyError as exc:

            logger.exception(
                "Database connection failed"
            )

            raise DatabaseInitializationError(
                f"Connection failed: {exc}"
            ) from exc

    @staticmethod
    def create_tables() -> None:
        """
        Create ORM tables.
        """

        try:

            logger.info(
                "Creating database tables..."
            )

            Base.metadata.create_all(
                bind=engine
            )

            logger.success(
                "Database tables created successfully"
            )

        except SQLAlchemyError as exc:

            logger.exception(
                "Table creation failed"
            )

            raise DatabaseInitializationError(
                f"Table creation failed: {exc}"
            ) from exc

    @staticmethod
    def show_registered_models() -> None:
        """
        Log all discovered ORM models.
        """

        logger.info(
            "Registered ORM Models:"
        )

        for table_name in Base.metadata.tables.keys():

            logger.info(
                f" - {table_name}"
            )

    def initialize(self) -> None:
        """
        Full database bootstrap process.
        """

        logger.info(
            "=" * 60
        )

        logger.info(
            f"{APPLICATION_NAME} Database Initialization"
        )

        logger.info(
            "=" * 60
        )

        self.validate_connection()

        self.show_registered_models()

        self.create_tables()

        logger.success(
            "Database initialization completed"
        )

        logger.info(
            "=" * 60
        )


def init_db() -> None:
    """
    Public initialization API.

    Safe to call from:
    - FastAPI lifespan
    - Startup event
    - Unit tests
    - CLI commands
    """

    DatabaseInitializer().initialize()


if __name__ == "__main__":

    try:

        init_db()

    except Exception as exc:

        logger.exception(
            f"Initialization failed: {exc}"
        )

        raise