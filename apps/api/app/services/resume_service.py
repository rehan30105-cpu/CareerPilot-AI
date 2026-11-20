"""Resume business logic: upload validation, PDF analysis orchestration.

This module contains the orchestration logic that:
1. Validates and stores uploaded resume files
2. Extracts text from PDFs
3. Invokes the AI service to generate analysis
4. Stores analysis results in the database
"""

import json
import logging
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume, ResumeAnalysis
from app.services.llm import LLMServiceError, OllamaUnavailableError
from app.services.parsing import extract_text_with_fallback
from app.schemas.resume import AnalysisResult

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"application/pdf"}
PDF_SIGNATURE = b"%PDF-"

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


def is_valid_pdf(buffer: bytes) -> bool:
    """Check if buffer starts with a valid PDF magic number."""
    if len(buffer) < 5:
        return False
    return buffer[:5] == PDF_SIGNATURE


async def get_resume_by_id(
    db: AsyncSession, resume_id: str, user_id: int
) -> Resume | None:
    """Retrieve a resume by ID, verifying ownership."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_resume_or_404(
    db: AsyncSession, resume_id: str, user_id: int
) -> Resume:
    """Retrieve a resume or raise 404."""
    resume = await get_resume_by_id(db, resume_id, user_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
    return resume


async def delete_resume(
    db: AsyncSession, resume_id: str, user_id: int
) -> bool:
    """Delete a resume and its associated analyses.

    Returns True if deleted, False if not found.
    """
    resume = await get_resume_by_id(db, resume_id, user_id)
    if resume is None:
        return False

    # Delete the stored file
    try:
        file_path = UPLOAD_DIR / resume.stored_filename
        if file_path.exists():
            file_path.unlink()
    except Exception:
        logger.warning(
            "Failed to delete resume file",
            extra={"resume_id": resume.id, "filename": resume.stored_filename},
        )

    await db.delete(resume)
    await db.commit()

async def upload_resume(
    db: AsyncSession,
    user_id: int,
    content: bytes,
    original_filename: str,
) -> Resume:
    """Validate and store an uploaded resume file.

    Returns the created Resume record.
    """
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10 MB.",
        )

    # Validate original filename
    if not original_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted.",
        )

    # Validate actual file signature
    if not is_valid_pdf(content):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid PDF file.",
        )

    # Store the file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / stored_filename
    file_path.write_bytes(content)

    # Create the database record
    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=len(content),
        mime_type="application/pdf",
        upload_status="uploaded",
    )
    logger.info(
        "Resume uploaded",
        extra={"resume_id": resume.id, "user_id": user_id, "filename": original_filename},
    )
    return resume


async def analyze_resume(
    db: AsyncSession,
    resume_id: str,
    user_id: int,
) -> ResumeAnalysis:
    """Run AI analysis on a resume.

    Steps:
    1. Retrieve the resume and verify ownership
    2. Extract text from the PDF
    3. Call the LLM service for structured analysis
    4. Store the analysis result

    Returns:
        The created ResumeAnalysis record.
    """
    resume = await get_resume_by_id(db, resume_id, user_id)
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # Check if PDF has readable text
    pdf_result = extract_text_with_fallback(
        Path(UPLOAD_DIR) / resume.stored_filename
    )

    if pdf_result.empty:
        resume.upload_status = "error"
        resume.extracted_text = None
        resume.page_count = 0
        resume.error_message = "PDF contains no readable text (possibly scanned)"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PDF contains no readable text. This may be a scanned document.",
        )

    # Store extracted text
    resume.extracted_text = pdf_result.text
    resume.page_count = pdf_result.page_count
    resume.has_scanned_content = pdf_result.has_scanned_content
    resume.upload_status = "analyzed"
    await db.commit()

    # Run LLM analysis
    try:
        analysis_result = await llm_service.generate_json(
            resume_text=pdf_result.text,
            schema=AnalysisResult,
        )
    except OllamaUnavailableError as exc:
        resume.upload_status = "error"
        resume.error_message = f"AI analysis unavailable: {exc}"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI analysis unavailable: {exc}",
        ) from exc
    except LLMServiceError as exc:
        resume.upload_status = "error"
        resume.error_message = f"Analysis failed: {exc}"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {exc}",
        ) from exc

    # Store the analysis
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        model_name="qwen3:4b",
        status="completed",
        structured_data=analysis_result.model_dump_json(),
        raw_response=json.dumps(analysis_result.model_dump()),
        response_time_ms=0,
        token_count=0,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return analysis

    return True
