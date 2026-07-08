from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import pandas as pd

from fastapi import UploadFile

from loguru import logger


# =====================================================
# STORAGE RESULT MODEL
# =====================================================

@dataclass(slots=True)
class StoredFile:
    """
    Metadata returned after file storage.
    """

    original_filename: str
    stored_filename: str
    file_path: str
    file_size_bytes: int
    file_hash: str


# =====================================================
# FILE STORAGE SERVICE
# =====================================================

class FileStorageService:
    """
    Enterprise File Storage Service

    Responsibilities
    ----------------
    - Save uploaded files
    - Validate uploads
    - Generate unique filenames
    - Track file metadata
    - Load DataFrames
    - Delete files
    - Storage monitoring

    Future Extensions
    -----------------
    - AWS S3
    - Azure Blob Storage
    - Google Cloud Storage
    """

    STORAGE_DIR = Path(
        "storage/uploads"
    )

    MAX_FILE_SIZE_MB = 100

    ALLOWED_EXTENSIONS = {
        ".csv",
        ".xlsx",
        ".xls"
    }

    ALLOWED_CONTENT_TYPES = {
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    def __init__(self) -> None:

        self.STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "FileStorageService initialized"
        )

    # =====================================================
    # SAVE FILE
    # =====================================================

    async def save_file(
        self,
        file: UploadFile
    ) -> StoredFile:

        filename = self._get_filename(
            file
        )

        self._validate_file(
            file,
            filename
        )

        content = await file.read()

        file_size = len(
            content
        )

        self._validate_size(
            file_size
        )

        extension = (
            Path(filename)
            .suffix
            .lower()
        )

        stored_filename = (
            f"{uuid4()}"
            f"{extension}"
        )

        file_path = (
            self.STORAGE_DIR
            / stored_filename
        )

        file_path.write_bytes(
            content
        )

        file_hash = sha256(
            content
        ).hexdigest()

        logger.success(
            f"File stored | "
            f"name={filename} | "
            f"size={file_size} bytes"
        )

        return StoredFile(
            original_filename=filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            file_hash=file_hash
        )

    # =====================================================
    # LOAD DATAFRAME
    # =====================================================

    def load_dataframe(
        self,
        file_path: str
    ) -> pd.DataFrame:

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(
                f"File not found: "
                f"{file_path}"
            )

        extension = (
            path.suffix.lower()
        )

        logger.info(
            f"Loading dataframe "
            f"from {file_path}"
        )

        if extension == ".csv":

            dataframe = pd.read_csv(
                path,
                low_memory=False
            )

        elif extension in {
            ".xlsx",
            ".xls"
        }:

            dataframe = pd.read_excel(
                path
            )

        else:

            raise ValueError(
                f"Unsupported file format: "
                f"{extension}"
            )

        logger.success(
            f"DataFrame loaded | "
            f"rows={len(dataframe)} | "
            f"columns={len(dataframe.columns)}"
        )

        return dataframe

    # =====================================================
    # DELETE FILE
    # =====================================================

    def delete_file(
        self,
        file_path: str
    ) -> bool:

        path = Path(file_path)

        if not path.exists():

            logger.warning(
                f"File not found: "
                f"{file_path}"
            )

            return False

        path.unlink()

        logger.info(
            f"Deleted file: "
            f"{file_path}"
        )

        return True

    # =====================================================
    # FILE INFORMATION
    # =====================================================

    def get_file_info(
        self,
        file_path: str
    ) -> dict:

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(
                file_path
            )

        stats = path.stat()

        return {

            "file_name":
                path.name,

            "file_size_bytes":
                stats.st_size,

            "created_at":
                stats.st_ctime,

            "modified_at":
                stats.st_mtime
        }

    # =====================================================
    # STORAGE METRICS
    # =====================================================

    def get_storage_summary(
        self
    ) -> dict:

        files = list(
            self.STORAGE_DIR.glob("*")
        )

        total_size = sum(
            file.stat().st_size
            for file in files
        )

        return {

            "total_files":
                len(files),

            "total_size_mb":
                round(
                    total_size
                    / (1024 * 1024),
                    2
                )
        }

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def _get_filename(
        file: UploadFile
    ) -> str:

        if not file.filename:

            raise ValueError(
                "Uploaded file "
                "filename is missing"
            )

        return file.filename

    def _validate_file(
        self,
        file: UploadFile,
        filename: str
    ) -> None:

        extension = (
            Path(filename)
            .suffix
            .lower()
        )

        if extension not in (
            self.ALLOWED_EXTENSIONS
        ):

            raise ValueError(
                f"Unsupported extension: "
                f"{extension}"
            )

        if (
            file.content_type
            and file.content_type
            not in self.ALLOWED_CONTENT_TYPES
        ):

            raise ValueError(
                f"Unsupported content type: "
                f"{file.content_type}"
            )

    def _validate_size(
        self,
        size_bytes: int
    ) -> None:

        max_size_bytes = (
            self.MAX_FILE_SIZE_MB
            * 1024
            * 1024
        )

        if size_bytes > max_size_bytes:

            raise ValueError(
                f"File exceeds "
                f"{self.MAX_FILE_SIZE_MB} MB"
            )