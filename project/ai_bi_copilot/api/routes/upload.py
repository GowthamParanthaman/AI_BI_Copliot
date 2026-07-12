from __future__ import annotations

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from time import perf_counter

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status
)

from loguru import logger

from api.dependencies.services import (
    get_dataset_service
)

from api.schemas.upload import (
    DatasetUploadResponse
)

from database.schemas.dataset_create import (
    DatasetCreate
)

from services.dataset_service import (
    DatasetService
)

from services.file_storage_service import (
    FileStorageService
)

from services.dataframe_service import (
    DataFrameService
)

from services.chat_indexing_service import (
    ChatIndexingService
)

router = APIRouter(
    prefix="/upload",
    tags=["Dataset Upload"]
)



file_storage_service = FileStorageService()

dataframe_service = DataFrameService()

chat_indexing_service = ChatIndexingService()

def json_serializer(obj):

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return float(obj)

    if isinstance(obj, np.bool_):
        return bool(obj)

    return str(obj)

@router.post(
    "/dataset",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Business Dataset"
)
async def upload_dataset(
    dataset_name: str = Form(...),
    uploaded_by: str | None = Form(None),
    department: str | None = Form(None),
    business_domain: str | None = Form(None),
    file: UploadFile = File(...),
    dataset_service: DatasetService = Depends(
        get_dataset_service
    )
) -> DatasetUploadResponse:

    start_time = perf_counter()

    stored_file = None

    try:

        logger.info(
            f"Dataset upload started: "
            f"{dataset_name}"
        )

        # =====================================
        # VALIDATE FILENAME
        # =====================================

        if not file.filename:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing"
            )

        # =====================================
        # DUPLICATE CHECK
        # =====================================

        existing = next(
            (
                dataset
                for dataset
                in dataset_service.get_all_datasets()
                if dataset.dataset_name == dataset_name
            ),
            None
        )

        if existing:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Dataset already exists: "
                    f"{dataset_name}"
                )
            )

        # =====================================
        # STORE FILE
        # =====================================

        stored_file = await (
            file_storage_service
            .save_file(file)
        )

        file_path = stored_file.file_path

        # =====================================
        # LOAD DATAFRAME
        # =====================================

        dataframe = (
            file_storage_service
            .load_dataframe(
                file_path
            )
        )

        # =====================================
        # DATA PROFILING
        # =====================================

        profile = (
            dataframe_service
            .profile_dataframe(
                dataframe
            )
        )

        schema = (
            dataframe_service
            .get_schema(
                dataframe
            )
        )

        quality_score = (
            dataframe_service
            .calculate_quality_score(
                dataframe
            )
        )

        duplicate_rows = int(
            dataframe
            .duplicated()
            .sum()
        )

        missing_values = int(
            dataframe
            .isna()
            .sum()
            .sum()
        )

        # =====================================
        # CREATE DATASET PAYLOAD
        # =====================================

        payload = DatasetCreate(

            dataset_name=dataset_name,

            file_name=file.filename,

            file_type=Path(
                file.filename
            ).suffix[1:].lower(),

            file_path=file_path,

            file_size_mb=round(
                stored_file.file_size_bytes
                / (1024 * 1024),
                4
            ),

            row_count=profile[
                "row_count"
            ],

            column_count=profile[
                "column_count"
            ],

            missing_values_count=
                missing_values,

            duplicate_rows_count=
                duplicate_rows,

            quality_score=
                quality_score,

            schema_metadata_json=json.dumps(
                    schema,
                    default=json_serializer
                ),

            profile_metadata_json=json.dumps(
                profile,
                default=json_serializer
            ),
            uploaded_by=
                uploaded_by,

            department=
                department,

            business_domain=
                business_domain
        )

        # =====================================
        # SAVE DATASET
        # =====================================

        dataset = (
            dataset_service
            .create_dataset(
                payload
            )
        )

        execution_time = round(
            perf_counter()
            - start_time,
            4
        )

        logger.success(
            f"Dataset uploaded "
            f"successfully "
            f"ID={dataset.id}"
        )
        # =====================================
        # BUILD AI CHAT RAG INDEX (best-effort)
        # =====================================

        try:

            chat_indexing_service.index_dataset(
                dataset_name=dataset.dataset_name,
                schema=schema,
                row_count=dataset.row_count,
                column_count=dataset.column_count,
                quality_score=dataset.quality_score,
                business_domain=dataset.business_domain,
            )

        except Exception:

            logger.exception(
                "AI Chat indexing failed after upload "
                "(non-blocking)"
            )


        return DatasetUploadResponse(

            success=True,

            dataset_id=
                dataset.id,

            dataset_name=
                dataset.dataset_name,

            row_count=
                dataset.row_count,

            column_count=
                dataset.column_count,

            quality_score=
                dataset.quality_score,

            file_path=dataset.file_path or "",

            execution_time_seconds=
                execution_time,

            uploaded_at=
                datetime.utcnow()
        )

    except HTTPException:

        raise

    except Exception as exc:

        logger.exception(
            "Dataset upload failed"
        )

        # =====================================
        # ROLLBACK FILE
        # =====================================

        if stored_file:

            try:

                file_storage_service.delete_file(
                    stored_file.file_path
                )

            except Exception:

                logger.warning(
                    "File rollback failed"
                )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )