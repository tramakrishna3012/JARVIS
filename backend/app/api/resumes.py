"""
Resumes API Routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.schemas.resume import (
    ResumeCreate, ResumeGenerate, ResumeUpdate, ResumeResponse, ATSAnalysis
)


router = APIRouter()


@router.get("", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all resumes for current user"""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id, Resume.is_archived == False)
        .order_by(Resume.updated_at.desc())
    )
    resumes = result.scalars().all()
    
    return [ResumeResponse.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get resume details"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return ResumeResponse.model_validate(resume)


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new resume manually"""
    resume = Resume(
        user_id=current_user.id,
        name=resume_data.name,
        is_master=resume_data.is_master,
        content=resume_data.content.model_dump(),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    return ResumeResponse.model_validate(resume)


@router.post("/generate", response_model=ResumeResponse)
async def generate_resume(
    request: ResumeGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a tailored resume for a job using AI"""
    # Get the target job
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create resume entry
    resume = Resume(
        user_id=current_user.id,
        name=request.name or f"Resume for {job.title} at {job.company}",
        target_job_id=job.id,
        target_job_title=job.title,
        target_company=job.company,
        content={},  # Will be populated by AI service
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    # Queue AI generation in background
    # background_tasks.add_task(resume_builder.generate, resume.id, current_user.id, request)
    
    return ResumeResponse.model_validate(resume)


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update resume"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    update_data = resume_data.model_dump(exclude_unset=True)
    if 'content' in update_data and update_data['content']:
        update_data['content'] = update_data['content'].model_dump()
    
    for field, value in update_data.items():
        setattr(resume, field, value)
    
    # Increment version on content changes
    if 'content' in update_data:
        resume.version += 1
    
    await db.commit()
    await db.refresh(resume)
    
    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download resume as PDF"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not resume.pdf_content:
        raise HTTPException(status_code=404, detail="PDF not generated yet")
    
    return StreamingResponse(
        io.BytesIO(resume.pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={resume.name}.pdf"}
    )


@router.post("/{resume_id}/analyze", response_model=ATSAnalysis)
async def analyze_resume_ats(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze resume for ATS compatibility"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # This would call the ATS analysis service
    # analysis = await ats_analyzer.analyze(resume)
    
    return ATSAnalysis(
        score=85,
        issues=["Consider adding more keywords"],
        suggestions=["Add quantifiable achievements"],
        missing_keywords=["kubernetes", "docker"],
        format_issues=[]
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive a resume (soft delete)"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume.is_archived = True
    await db.commit()
