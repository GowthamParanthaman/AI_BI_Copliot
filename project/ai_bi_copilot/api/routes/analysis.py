from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from dataclasses import asdict

from loguru import logger

from api.dependencies.services import (
    get_bi_service,
    get_dataset_service
)

from api.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse
)

from services.bi_service import BIService
from services.dataset_service import DatasetService

from services.file_storage_service import (
    FileStorageService
)
from time import perf_counter

router = APIRouter(
    prefix="/analysis",
    tags=["Business Intelligence"]
)
file_storage_service = (
    FileStorageService()
)


@router.post(
    "/run",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute AI Business Intelligence Workflow",
    description="""
    Execute the complete AI BI Copilot workflow.

    Workflow:
        Dataset
            ↓
        Analysis Agent
            ↓
        KPI Agent
            ↓
        Insight Agent
            ↓
        Recommendation Agent
            ↓
        Report Agent
            ↓
        Visualization Agent
            ↓
        Chat Agent
    """
)
async def run_analysis(
    request: AnalysisRequest,
    bi_service: BIService = Depends(
        get_bi_service
    ),
    dataset_service: DatasetService = Depends(
        get_dataset_service
    )
) -> AnalysisResponse:

    execution_id = str(
        uuid4()
    )

    logger.info(
        f"[{execution_id}] "
        f"Analysis request received "
        f"for dataset={request.dataset_name}"
    )
    dataset = None
    try:

        # =====================================================
        # DATASET VALIDATION
        # =====================================================

        dataset = (
            dataset_service
            .get_dataset_by_name(
                request.dataset_name
            )
        )

        if dataset is None:

            logger.warning(
                f"[{execution_id}] "
                f"Dataset not found: "
                f"{request.dataset_name}"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Dataset not found: "
                    f"{request.dataset_name}"
                )
            )

        if not dataset.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Dataset is inactive: "
                    f"{dataset.dataset_name}"
                )
            )

        if not dataset.file_path:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset file path missing"
            )

        # =====================================================
        # UPDATE ANALYSIS STATUS
        # =====================================================

        dataset.analysis_status = (
            "IN_PROGRESS"
        )

        dataset_service.db.commit()

        # =====================================================
        # LOAD DATAFRAME
        # =====================================================

        dataframe = (
            file_storage_service
            .load_dataframe(
                dataset.file_path
            )
        )

        if dataframe.empty:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset is empty"
            )

        logger.info(
            f"[{execution_id}] "
            f"Dataframe loaded | "
            f"Rows={len(dataframe)} | "
            f"Columns={len(dataframe.columns)}"
        )

        # =====================================================
        # EXECUTE BI WORKFLOW
        # =====================================================

        workflow_start = perf_counter()

        result = (
            bi_service
            .run_pipeline(
                dataframe=dataframe,
                dataset_name=dataset.dataset_name,
                question=request.question
            )
        )

        execution_time = round(
            perf_counter() - workflow_start,
            4
        )

        # =====================================================
        # UPDATE DATASET METADATA
        # =====================================================

        dataset.analysis_status = (
            "COMPLETED"
        )

        dataset.analysis_count += 1

        dataset.last_analyzed_at = (
            datetime.utcnow()
        )

        dataset.last_execution_time_seconds = (
            execution_time
        )

        dataset_service.db.commit()

        logger.success(
            f"[{execution_id}] "
            f"Analysis completed | "
            f"Dataset={dataset.dataset_name} | "
            f"Runtime={execution_time}s"
        )
        
        # =====================================================
        # DEBUG
        # =====================================================

        logger.info(
            f"RESULT INSIGHTS = {result.get('insights')}"
        )

        logger.info(
            f"RESULT INSIGHTS TYPE = {type(result.get('insights'))}"
        )

        logger.info(
            f"RESULT RECOMMENDATIONS = {result.get('recommendations')}"
        )

        logger.info(
            f"RESULT RECOMMENDATIONS TYPE = {type(result.get('recommendations'))}"
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        business_analysis = result.get(
            "business_analysis"
        )

        business_analysis_dict = (
            asdict(business_analysis)
            if business_analysis is not None
            else {}
        )

        return AnalysisResponse(

            success=True,

            execution_id=
                result.get(
                    "execution_id"
                ),

            execution_status=
                result.get(
                    "execution_status",
                    "SUCCESS"
                ),

            execution_time_seconds=
                execution_time,

            generated_at=
                datetime.utcnow(),

            dataset_name=
                dataset.dataset_name,

            kpis=
                result.get(
                    "kpis"
                ),

            forecast_results=
                result.get(
                    "forecast_results",
                    {}
                ),

            anomalies=
                result.get(
                    "anomalies",
                    []
                ),

            root_causes=
                result.get(
                    "root_causes",
                    {}
                ),

            health_score=
                result.get(
                    "health_score",
                    {}
                ),

            alerts=
                result.get(
                    "alerts",
                    {}
                ),

            insights=
                result.get(
                    "insights",
                    {}
                ),

            recommendations=
                result.get(
                    "recommendations",
                    {}
                ),

            action_plan=
                result.get(
                    "action_plan",
                    {}
                ),

            business_analysis=
                business_analysis_dict,

            dashboard=
                result.get(
                    "dashboard",
                    {}
                ),

            report=
                result.get(
                    "report"
                ),

            visualizations=
                result.get(
                    "visualizations",
                    []
                ),
                
            chart_paths=
                result.get(
                    "chart_paths",
                    []
                ),

            chart_metadata=
                result.get(
                    "chart_metadata",
                    []
                ),    

            agent_metrics=
                result.get(
                    "agent_metrics",
                    {}
                ),

            agent_errors=
                result.get(
                    "agent_errors",
                    []
                ),
                
            report_pdf_path=result.get(
                    "report_pdf_path"
                ),    

            error=None,
        )

    except HTTPException:

        raise

    except Exception as exc:

        logger.exception(
            f"[{execution_id}] "
            f"Workflow execution failed"
        )

        try:

            if dataset:

                dataset.analysis_status = (
                    "FAILED"
                )

                dataset_service.db.commit()

        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "execution_id":
                    execution_id,

                "message":
                    "Analysis execution failed",

                "timestamp":
                    datetime.utcnow()
                    .isoformat(),

                "error":
                    str(exc),
            },
        )