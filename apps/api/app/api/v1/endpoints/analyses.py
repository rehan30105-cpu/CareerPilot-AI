"""Analysis result API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db_session
from app.models.resume import Resume, ResumeAnalysis
from app.schemas.resume import AnalysisBrief, AnalysisListResponse

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.get("/{analysis_id}", response_model=AnalysisBrief)
async def get_analysis(
    analysis_id: str,
    current_user: Annotated[
        "app.models.user.User", Depends(get_current_active_user)
    ] = None,
    db: Annotated[
        "AsyncSession", Depends(get_db_session)
    ] = None,
):
    """Retrieve a single analysis result."""
    result = await db.execute(
        select(ResumeAnalysis)
        .where(
            ResumeAnalysis.id == analysis_id,
            ResumeAnalysis.resume_id.in_(
                select(Resume.id).where(Resume.user_id == current_user.id)
            ),
        )
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    return analysis
