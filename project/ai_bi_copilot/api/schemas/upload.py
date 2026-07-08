from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class DatasetUploadResponse(BaseModel):

    success: bool = Field(...)

    dataset_id: int = Field(...)

    dataset_name: str = Field(...)

    row_count: int = Field(...)

    column_count: int = Field(...)

    quality_score: float = Field(...)

    file_path: str = Field(...)

    execution_time_seconds: float = Field(...)

    uploaded_at: datetime = Field(...)