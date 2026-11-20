"""Pydantic schemas for resume and analysis endpoints."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.resume import Resume, ResumeAnalysis


class FileType(str, Enum):
    """Accepted file types."""

    PDF = "application/pdf"


class ResumeUploadResponse(BaseModel):
    """Response for resume upload."""

    id: str
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    upload_status: str

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Paginated list of resumes for a user."""

    resumes: list[Resume]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ResumeReadResponse(BaseModel):
    """A single resume with its analyses."""

    id: str
    original_filename: str
    stored_filename: str
    mime_type: str
    file_size: int
    upload_status: str
    page_count: int | None
    uploaded_at: datetime
    analyses: list["ResumeAnalysisBrief"] = []

    class Config:
        from_attributes = True


class ResumeAnalysisBrief(BaseModel):
    """Brief summary of an analysis."""

    id: str
    model_name: str
    status: str
    created_at: datetime
    response_time_ms: int | None
    token_count: int | None

    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    """Structured AI analysis result."""

    candidate_name: str | None = None
    professional_summary: str | None = None
    education: list[str] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    internships: list[dict[str, Any]] = Field(default_factory=list)
    work_experience: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_improvements: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    """Response for analysis endpoint."""

    analysis: AnalysisResult
    model_name: str
    created_at: datetime
    response_time_ms: int | None
    token_count: int | None

    class Config:
        from_attributes = True


class AnalysisBrief(BaseModel):
    """Brief analysis summary for the analyses list."""

    id: str
    model_name: str
    status: str
    created_at: datetime
    candidate_name: str | None = None

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Paginated list of analyses for a resume."""

    analyses: list[AnalysisBrief]
    total: int
    resume_id: str

    class Config:
        from_attributes = True


def _write_uploaded_file(content: bytes, filename: str) -> str:
    """Write uploaded file to a safe, unique storage path.

    Uses a unique UUID filename so the original filename cannot influence
    the storage path. The base directory is configurable via the
    RESUME_UPLOAD_DIR environment variable (defaults to an OS-specific
    data directory outside the web root).
    """
    upload_dir = (
        Path(__file__).resolve().parent.parent.parent
        / "uploads"
    )
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}.pdf"
    file_path = upload_dir / stored_filename

    file_path.write_bytes(content)
    return str(file_path)
