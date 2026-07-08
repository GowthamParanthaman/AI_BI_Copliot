from __future__ import annotations

from typing import List
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from database.models.dataset import Dataset
from database.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    """
    Repository responsible for Dataset persistence operations.

    Contains only Dataset-specific queries.

    Common CRUD operations are inherited from BaseRepository.
    """

    def __init__(
        self,
        db: Session
    ) -> None:

        super().__init__(
            model=Dataset,
            db=db
        )

    # =====================================================
    # SINGLE DATASET QUERIES
    # =====================================================

    def get_by_dataset_id(
        self,
        dataset_id: int
    ) -> Optional[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(Dataset.id == dataset_id)
            .first()
        )

    def get_by_name(
        self,
        dataset_name: str
    ) -> Optional[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.dataset_name == dataset_name
            )
            .first()
        )

    # =====================================================
    # ACTIVE DATASETS
    # =====================================================

    def get_active_datasets(
        self
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.is_active.is_(True)
            )
            .all()
        )

    # =====================================================
    # BUSINESS DOMAIN FILTERS
    # =====================================================

    def get_by_business_domain(
        self,
        domain: str
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.business_domain == domain
            )
            .all()
        )

    # =====================================================
    # PIPELINE STATUS QUERIES
    # =====================================================

    def get_by_ingestion_status(
        self,
        status: str
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.ingestion_status == status
            )
            .all()
        )

    def get_by_cleaning_status(
        self,
        status: str
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.cleaning_status == status
            )
            .all()
        )

    def get_by_schema_status(
        self,
        status: str
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.schema_status == status
            )
            .all()
        )

    def get_by_analysis_status(
        self,
        status: str
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.analysis_status == status
            )
            .all()
        )

    # =====================================================
    # AGENT WORK QUEUES
    # =====================================================

    def get_pending_analysis(
        self
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.analysis_status == "PENDING"
            )
            .all()
        )

    def get_pending_cleaning(
        self
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.cleaning_status == "PENDING"
            )
            .all()
        )

    def get_pending_schema_validation(
        self
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.schema_status == "PENDING"
            )
            .all()
        )

    # =====================================================
    # DASHBOARD QUERIES
    # =====================================================

    def get_recent_datasets(
        self,
        limit: int = 10
    ) -> List[Dataset]:

        return (
            self.db.query(Dataset)
            .order_by(
                desc(Dataset.created_at)
            )
            .limit(limit)
            .all()
        )

    def get_latest_dataset(
        self
    ) -> Optional[Dataset]:

        return (
            self.db.query(Dataset)
            .order_by(
                desc(Dataset.created_at)
            )
            .first()
        )

    # =====================================================
    # SOFT DELETE
    # =====================================================

    def deactivate_dataset(
        self,
        dataset_id: int
    ) -> Optional[Dataset]:

        dataset = self.get_by_dataset_id(
            dataset_id
        )

        if dataset is None:
            return None

        dataset.is_active = False

        self.db.commit()
        self.db.refresh(dataset)

        return dataset

    # =====================================================
    # STATISTICS
    # =====================================================

    def count_active_datasets(
        self
    ) -> int:

        return (
            self.db.query(Dataset)
            .filter(
                Dataset.is_active.is_(True)
            )
            .count()
        )

    def count_all_datasets(
        self
    ) -> int:

        return (
            self.db.query(Dataset)
            .count()
        )