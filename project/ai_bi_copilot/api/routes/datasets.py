from __future__ import annotations

from typing import Any, List

from loguru import logger

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from services.dataset_service import (
    DatasetService
)

from services.file_storage_service import (
    FileStorageService
)

from api.dependencies.services import (
    get_dataset_service
)

from database.schemas import (
    DatasetCreate,
    DatasetResponse
)


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)

_file_storage = FileStorageService()


# =====================================================
# CREATE DATASET
# =====================================================

@router.post(
    "/",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Dataset",
    description="Create a new dataset metadata record."
)
def create_dataset(
    payload: DatasetCreate,
    service: DatasetService = Depends(
        get_dataset_service
    )
) -> DatasetResponse:

    try:

        logger.info(
            f"Creating dataset: "
            f"{payload.dataset_name}"
        )

        dataset = service.create_dataset(
            payload
        )

        return DatasetResponse.model_validate(
            dataset
        )

    except ValueError as exc:

        logger.warning(str(exc))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    except Exception as exc:

        logger.exception(exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


# =====================================================
# GET ALL DATASETS
# =====================================================

@router.get(
    "/",
    response_model=List[DatasetResponse],
    summary="Get Datasets",
    description="Retrieve all datasets."
)
def get_datasets(
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000
    ),
    service: DatasetService = Depends(
        get_dataset_service
    )
) -> List[DatasetResponse]:

    try:

        datasets = service.get_all_datasets()

        return [
            DatasetResponse.model_validate(
                item
            )
            for item in datasets
        ]

    except Exception as exc:

        logger.exception(exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch datasets"
        )


# =====================================================
# GET DATASET BY ID
# =====================================================

@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Get Dataset",
    description="Retrieve dataset by ID."
)
def get_dataset(
    dataset_id: int,
    service: DatasetService = Depends(
        get_dataset_service
    )
) -> DatasetResponse:

    dataset = service.get_dataset(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found"
        )

    return DatasetResponse.model_validate(
        dataset
    )


# =====================================================
# GET ACTIVE DATASETS
# =====================================================

@router.get(
    "/active/list",
    response_model=List[DatasetResponse],
    summary="Active Datasets",
    description="Retrieve active datasets."
)
def get_active_datasets(
    service: DatasetService = Depends(
        get_dataset_service
    )
):

    datasets = (
        service.get_active_datasets()
    )

    return [
        DatasetResponse.model_validate(
            item
        )
        for item in datasets
    ]


# =====================================================
# DATASET SUMMARY
# =====================================================

@router.get(
    "/summary/stats",
    summary="Dataset Summary"
)
def get_dataset_summary(
    service: DatasetService = Depends(
        get_dataset_service
    )
):

    return service.get_dataset_summary()




# =====================================================
# GET DATASET ROWS
# =====================================================

@router.get(
    "/{dataset_name}/rows",
    summary="Get Dataset Rows",
    description="Return the actual rows of an uploaded dataset as JSON records."
)
def get_dataset_rows(
    dataset_name: str,
    limit: int = Query(
        default=5000,
        ge=1,
        le=50000,
        description="Maximum rows to return"
    ),
    service: DatasetService = Depends(
        get_dataset_service
    )
) -> dict[str, Any]:

    dataset = service.get_dataset_by_name(dataset_name)

    if dataset is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset not found: {dataset_name}"
        )

    if not dataset.file_path:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file path missing"
        )

    try:

        df = _file_storage.load_dataframe(dataset.file_path)
        total_rows = len(df)
        df = df.head(limit)

        # Replace NaN/NaT with None for clean JSON
        rows: list[dict[str, Any]] = (
            df.where(df.notna(), other=None)
            .to_dict(orient="records")
        )

        logger.info(
            f"Returning {len(rows)}/{total_rows} rows "
            f"for dataset={dataset_name}"
        )

        return {
            "dataset_name": dataset_name,
            "total_rows":   total_rows,
            "returned_rows": len(rows),
            "columns":      list(df.columns),
            "rows":         rows,
        }

    except FileNotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file not found on disk"
        )

    except Exception as exc:

        logger.exception(exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dataset rows"
        )

# =====================================================
# SOFT DELETE
# =====================================================

@router.delete(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Deactivate Dataset"
)
def deactivate_dataset(
    dataset_id: int,
    service: DatasetService = Depends(
        get_dataset_service
    )
):

    try:

        dataset = (
            service.deactivate_dataset(
                dataset_id
            )
        )

        return DatasetResponse.model_validate(
            dataset
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )