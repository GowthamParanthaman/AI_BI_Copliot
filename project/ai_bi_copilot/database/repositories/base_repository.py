from __future__ import annotations

from typing import Generic
from typing import Type
from typing import TypeVar
from typing import Optional
from typing import Sequence

from loguru import logger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Enterprise Base Repository

    Responsibilities:
    - Generic CRUD Operations
    - Transaction Management
    - Error Handling
    - Logging
    - Pagination
    """

    def __init__(
        self,
        model: Type[ModelType],
        db: Session
    ) -> None:

        self.model = model
        self.db = db

    # ==========================================
    # CREATE
    # ==========================================

    def create(
        self,
        entity: ModelType
    ) -> ModelType:

        try:

            self.db.add(entity)

            self.db.commit()

            self.db.refresh(entity)

            logger.info(
                f"{self.model.__name__} created successfully"
            )

            return entity

        except SQLAlchemyError as exc:

            self.db.rollback()

            logger.exception(exc)

            raise

    # ==========================================
    # BULK CREATE
    # ==========================================

    def create_many(
        self,
        entities: list[ModelType]
    ) -> list[ModelType]:

        try:

            self.db.add_all(entities)

            self.db.commit()

            logger.info(
                f"{len(entities)} "
                f"{self.model.__name__} records inserted"
            )

            return entities

        except SQLAlchemyError as exc:

            self.db.rollback()

            logger.exception(exc)

            raise

    # ==========================================
    # GET ALL
    # ==========================================

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[ModelType]:

        return (
            self.db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==========================================
    # COUNT
    # ==========================================

    def count(self) -> int:

        return (
            self.db.query(self.model)
            .count()
        )

    # ==========================================
    # UPDATE
    # ==========================================

    def update(
        self,
        entity: ModelType
    ) -> ModelType:

        try:

            self.db.commit()

            self.db.refresh(entity)

            logger.info(
                f"{self.model.__name__} updated successfully"
            )

            return entity

        except SQLAlchemyError as exc:

            self.db.rollback()

            logger.exception(exc)

            raise

    # ==========================================
    # DELETE
    # ==========================================

    def delete(
        self,
        entity: ModelType
    ) -> None:

        try:

            self.db.delete(entity)

            self.db.commit()

            logger.info(
                f"{self.model.__name__} deleted successfully"
            )

        except SQLAlchemyError as exc:

            self.db.rollback()

            logger.exception(exc)

            raise

    # ==========================================
    # SAVE
    # ==========================================

    def save(self) -> None:

        try:

            self.db.commit()

        except SQLAlchemyError as exc:

            self.db.rollback()

            logger.exception(exc)

            raise

    # ==========================================
    # REFRESH
    # ==========================================

    def refresh(
        self,
        entity: ModelType
    ) -> None:

        self.db.refresh(entity)

    # ==========================================
    # EXISTS
    # ==========================================

    def exists(
        self,
        entity_id: int
    ) -> bool:

        entity = (
            self.db.query(self.model)
            .filter(
                getattr(
                    self.model,
                    "id"
                ) == entity_id
            )
            .first()
        )

        return entity is not None

    # ==========================================
    # GET BY ID
    # ==========================================

    def get_by_id(
        self,
        entity_id: int
    ) -> Optional[ModelType]:

        return (
            self.db.query(self.model)
            .filter(
                getattr(
                    self.model,
                    "id"
                ) == entity_id
            )
            .first()
        )