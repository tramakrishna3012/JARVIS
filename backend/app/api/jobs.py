"""
Jobs API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job, JobStatus
from app.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobFilter,
    JobDiscoverRequest, JobDiscoverResponse
)


router = APIRouter()


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    country: Optional[str] = None,
    is_remote: Optional[bool] = None,
    min_score: Optional[float] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filters"""
    query = select(Job)
    
    # Apply filters
    conditions = []
    
    if status:
        conditions.append(Job.status == status)
    if country:
        conditions.append(Job.country.ilike(f"%{country}%"))
    if is_remote is not None:
        conditions.append(Job.is_remote == is_remote)
    if min_score is not None:
        conditions.append(Job.relevance_score >= min_score)
    if search:
        conditions.append(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Job.relevance_score.desc(), Job.discovered_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job details"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.model_validate(job)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually add a job"""
    job = Job(**job_data.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return JobResponse.model_validate(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update job status"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.delete(job)
    await db.commit()


@router.post("/discover", response_model=JobDiscoverResponse)
async def discover_jobs(
    request: JobDiscoverRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger job discovery from configured sources"""
    # This would trigger the job discovery service in the background
    # For now, return a placeholder response
    
    # background_tasks.add_task(job_discovery_service.discover, request, current_user.id)
    
    return JobDiscoverResponse(
        jobs_found=0,
        jobs_new=0,
        jobs_duplicate=0,
        status="discovery_started"
    )


@router.post("/{job_id}/score")
async def recalculate_job_score(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Recalculate relevance score for a job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # This would call the AI scoring service
    # score = await ai_engine.calculate_job_score(job, current_user)
    
    return {"message": "Score recalculation queued", "job_id": job_id}
