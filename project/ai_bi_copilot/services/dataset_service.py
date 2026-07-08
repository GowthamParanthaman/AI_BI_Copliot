from __future__ import annotations

from typing import List
from typing import Optional

from loguru import logger

from sqlalchemy.orm import Session

from database.models.dataset import Dataset

from database.repositories.dataset_repository import (
    DatasetRepository
)

from database.schemas.dataset_create import (
    DatasetCreate
)


class DatasetService:
    """
    Enterprise Dataset Service

    Responsibilities:
    - Business Validation
    - Dataset Lifecycle Management
    - Workflow Orchestration
    - Repository Coordination
    """

    def __init__(
        self,
        db: Session
    ) -> None:

        self.db = db

        self.repository = DatasetRepository(
            db
        )

    # =====================================================
    # CREATE DATASET
    # =====================================================

    def create_dataset(
        self,
        payload: DatasetCreate
    ) -> Dataset:

        logger.info(
            f"Creating dataset: "
            f"{payload.dataset_name}"
        )

        existing_dataset = (
            self.repository.get_by_name(
                payload.dataset_name
            )
        )

        if existing_dataset:

            raise ValueError(
                f"Dataset already exists: "
                f"{payload.dataset_name}"
            )

        dataset = Dataset(

            dataset_name=payload.dataset_name,

            file_name=payload.file_name,

            file_type=payload.file_type,

            file_size_mb=payload.file_size_mb,

            file_path=payload.file_path,

            row_count=payload.row_count,

            column_count=payload.column_count,

            missing_values_count=payload.missing_values_count,

            duplicate_rows_count=payload.duplicate_rows_count,

            quality_score=payload.quality_score,

            schema_json=payload.schema_metadata_json,

            profile_json=payload.profile_metadata_json,

            uploaded_by=payload.uploaded_by,

            department=payload.department,

            business_domain=payload.business_domain,

            semantic_description=payload.semantic_description,

            version=payload.version,
        )

        dataset = self.repository.create(
            dataset
        )

        logger.success(
            f"Dataset created successfully. "
            f"ID={dataset.id}"
        )

        return dataset

    # =====================================================
    # GET DATASET
    # =====================================================

    def get_dataset(
        self,
        dataset_id: int
    ) -> Optional[Dataset]:

        return (
            self.repository
            .get_by_dataset_id(
                dataset_id
            )
        )
    def get_dataset_by_name(
        self,
        dataset_name: str
    ) -> Optional[Dataset]:

        return (
            self.repository
            .get_by_name(
                dataset_name
            )
        )
    # =====================================================
    # GET ALL DATASETS
    # =====================================================

    def get_all_datasets(
        self
    ) -> List[Dataset]:

        return list(
            self.repository.get_all()
        )

    # =====================================================
    # ACTIVE DATASETS
    # =====================================================

    def get_active_datasets(
        self
    ) -> List[Dataset]:

        return list(
            self.repository
            .get_active_datasets()
        )

    # =====================================================
    # RECENT DATASETS
    # =====================================================

    def get_recent_datasets(
        self,
        limit: int = 10
    ) -> List[Dataset]:

        return list(
            self.repository
            .get_recent_datasets(
                limit=limit
            )
        )

    # =====================================================
    # DATASETS WAITING FOR ANALYSIS
    # =====================================================

    def get_pending_analysis(
        self
    ) -> List[Dataset]:

        return list(
            self.repository
            .get_pending_analysis()
        )

    # =====================================================
    # START INGESTION
    # =====================================================

    def start_ingestion(
        self,
        dataset_id: int
    ) -> Dataset:

        dataset = (
            self.repository
            .get_by_dataset_id(
                dataset_id
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        dataset.ingestion_status = (
            "IN_PROGRESS"
        )

        self.repository.update(
            dataset
        )

        logger.info(
            f"Ingestion started "
            f"for Dataset={dataset.id}"
        )

        return dataset

    # =====================================================
    # COMPLETE INGESTION
    # =====================================================

    def complete_ingestion(
        self,
        dataset_id: int
    ) -> Dataset:

        dataset = (
            self.repository
            .get_by_dataset_id(
                dataset_id
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        dataset.ingestion_status = (
            "COMPLETED"
        )

        self.repository.update(
            dataset
        )

        logger.success(
            f"Ingestion completed "
            f"for Dataset={dataset.id}"
        )

        return dataset

    # =====================================================
    # SOFT DELETE
    # =====================================================

    def deactivate_dataset(
        self,
        dataset_id: int
    ) -> Dataset:

        dataset = (
            self.repository
            .deactivate_dataset(
                dataset_id
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        logger.warning(
            f"Dataset deactivated "
            f"ID={dataset.id}"
        )

        return dataset

    # =====================================================
    # KPI DASHBOARD SUMMARY
    # =====================================================

    def get_dataset_summary(
        self
    ) -> dict:

        total_datasets = (
            self.repository
            .count_all_datasets()
        )

        active_datasets = (
            self.repository
            .count_active_datasets()
        )

        return {

            "total_datasets":
                total_datasets,

            "active_datasets":
                active_datasets,

            "inactive_datasets":
                total_datasets
                - active_datasets
        }