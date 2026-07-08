from __future__ import annotations

from typing import List

from loguru import logger

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from services.dataset_service import (
    DatasetService
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