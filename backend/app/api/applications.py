"""
Applications API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.application import (
    ApplicationCreate, ApplicationApply, ApplicationUpdate, 
    ApplicationResponse, ApplicationStats
)


router = APIRouter()


@router.get("", response_model=List[ApplicationResponse])
async def list_applications(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all applications"""
    query = select(Application).where(Application.user_id == current_user.id)
    
    if status:
        query = query.where(Application.status == status)
    
    query = query.order_by(Application.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return [ApplicationResponse.model_validate(app) for app in applications]


@router.get("/stats", response_model=ApplicationStats)
async def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get application statistics"""
    result = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    status_counts = dict(result.all())
    
    total = sum(status_counts.values())
    offered = status_counts.get(ApplicationStatus.OFFERED.value, 0)
    rejected = status_counts.get(ApplicationStatus.REJECTED.value, 0)
    
    return ApplicationStats(
        total=total,
        pending=status_counts.get(ApplicationStatus.PENDING.value, 0),
        submitted=status_counts.get(ApplicationStatus.SUBMITTED.value, 0),
        interviewing=status_counts.get(ApplicationStatus.INTERVIEWING.value, 0),
        offered=offered,
        rejected=rejected,
        acceptance_rate=round(offered / (offered + rejected) * 100, 2) if (offered + rejected) > 0 else 0
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get application details"""
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id, Application.user_id == current_user.id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return ApplicationResponse.model_validate(application)


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a manual application entry"""
    # Verify job exists
    result = await db.execute(select(Job).where(Job.id == app_data.job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")
    
    application = Application(
        user_id=current_user.id,
        **app_data.model_dump()
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    
    return ApplicationResponse.model_validate(application)


@router.post("/apply", response_model=ApplicationResponse)
async def auto_apply(
    request: ApplicationApply,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Automatically apply to a job"""
    # Verify job exists
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check for existing application
    result = await db.execute(
        select(Application)
        .where(Application.user_id == current_user.id, Application.job_id == request.job_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already applied to this job")
    
    # Create application
    application = Application(
        user_id=current_user.id,
        job_id=request.job_id,
        resume_id=request.resume_id,
        status=ApplicationStatus.PENDING.value,
        method="auto_form",
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    
    # Queue auto-apply in background
    # background_tasks.add_task(application_bot.apply, application.id)
    
    return ApplicationResponse.model_validate(application)


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    app_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update application status/details"""
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id, Application.user_id == current_user.id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = app_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(application, field, value)
    
    await db.commit()
    await db.refresh(application)
    
    return ApplicationResponse.model_validate(application)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an application"""
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id, Application.user_id == current_user.id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    await db.delete(application)
    await db.commit()
