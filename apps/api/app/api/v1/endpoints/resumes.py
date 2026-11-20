"""Resume management API endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.v1.deps import get_current_active_user, get_db_session
from app.models.resume import Resume
from app.services.resume_service import (
    analyze_resume,
    delete_resume,
    get_resume_by_id,
    get_resume_or_404,
    upload_resume,
)
from app.schemas.resume import (
    AnalysisBrief,
    AnalysisListResponse,
    ResumeListResponse,
    ResumeReadResponse,
    ResumeUploadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume_endpoint(
    file: UploadFile = File(..., description="PDF resume file"),
    current_user: Annotated[
        "app.models.user.User", Depends(get_current_active_user)
    ] = None,
    db: Annotated[
        "AsyncSession", Depends(get_db_session)
    ] = None,
):
    """Upload a resume PDF file.

    Accepts PDF files up to 10 MB. Stores the file outside the web root.
    """
    content = await file.read()

    resume = await upload_resume(
        db=db,
        user_id=current_user.id,
        content=content,
        original_filename=file.filename or "unnamed.pdf",
    )

    logger.info(
        "Resume uploaded via API",
        extra={"resume_id": resume.id, "user_id": current_user.id},
    )

    return resume


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    page: int = 1,
    page_size: int = 20,
    current_user: Annotated[
        "app.models.user.User", Depends(get_current_active_user)
    ] = None,
    db: Annotated[
        "AsyncSession", Depends(get_db_session)
    ] = None,
):
    """List all resumes for the authenticated user."""
    offset = (page - 1) * page_size

    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    resumes = result.scalars().all()

    total_result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id)
    )
    total = total_result.scalar() or 0

    return ResumeListResponse(
        resumes=resumes,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{resume_id}", response_model=ResumeReadResponse)
async def get_resume(
    resume_id: str,
    current_user: Annotated[
        "app.models.user.User", Depends(get_current_active_user)
    ] = None,
    db: Annotated[
        "AsyncSession", Depends(get_db_session)
    ] = None,
):
    """Get a single resume with its analysis history."""
    resume = await get_resume_or_404(db, resume_id, current_user.id)

    # Get analyses
    analyses_result = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.resume_id == resume.id)
        .order_by(ResumeAnalysis.created_at.desc())
    )
    analyses = analyses_result.scalars().all()

    return ResumeReadResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        stored_filename=resume.stored_filename,
        mime_type=resume.mime_type,
        file_size=resume.file_size,
        upload_status=resume.upload_status,
        page_count=resume.page_count,
        uploaded_at=resume.uploaded_at,
        analyses=analyses,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_endpoint(
    resume_id: str,
    current_user: Annotated[
        "app.models.user.User", Depends(get_current_active_user)
    ] = None,
    db: Annotated[
        "AsyncSession", Depends(get_db_session)
    ] = None,
):
    """Delete a resume and all its analyses."""
    deleted = await delete_resume(db, resume_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
    logger.info(
        "Resume deleted",
        extra={"resume_id": resume_id, "user_id": current_user.id},
    )
    return None


@router.post("/{resume_id}/analyze", response_model=AnalysisBrief)
async def analyze_resume_endpoint(
    resume_id: str,
    current_user: Annotated[
        "app.models.user.User", Depends(get_current_active_user)
    ] = None,
    db: Annotated[
        "AsyncSession", Depends(get_db_session)
    ] = None,
):
    """Run AI analysis on a resume.

    Triggers the LLM service to analyze the resume text and store the
    structured results.
    """
    analysis = await analyze_resume(db, resume_id, current_user.id)

    return AnalysisBrief(
        id=analysis.id,
        model_name=analysis.model_name,
        status=analysis.status,
        created_at=analysis.created_at,
        candidate_name=analysis.structured_data.get("candidate_name") if analysis.structured_data else None,
    )
