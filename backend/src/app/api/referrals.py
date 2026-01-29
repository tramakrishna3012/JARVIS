"""
Referrals API Routes
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.referral import Referral, Connection, ReferralStatus
from app.schemas.referral import (
    ConnectionCreate, ConnectionResponse, ConnectionSearch,
    ReferralCreate, ReferralUpdate, ReferralSend, ReferralResponse,
    ReferralMessageDraft
)


router = APIRouter()


# Connection endpoints
@router.get("/connections", response_model=List[ConnectionResponse])
async def list_connections(
    company: Optional[str] = None,
    is_recruiter: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List LinkedIn connections"""
    query = select(Connection).where(Connection.user_id == current_user.id)
    
    if company:
        query = query.where(Connection.current_company.ilike(f"%{company}%"))
    if is_recruiter is not None:
        query = query.where(Connection.is_recruiter == is_recruiter)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    connections = result.scalars().all()
    
    return [ConnectionResponse.model_validate(c) for c in connections]


@router.post("/connections/search", response_model=List[ConnectionResponse])
async def search_connections(
    search: ConnectionSearch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search connections at a specific company"""
    query = select(Connection).where(
        Connection.user_id == current_user.id,
        Connection.current_company.ilike(f"%{search.company}%")
    )
    
    if not search.include_recruiters:
        query = query.where(Connection.is_recruiter == False)
    if not search.include_hiring_managers:
        query = query.where(Connection.is_hiring_manager == False)
    
    result = await db.execute(query)
    connections = result.scalars().all()
    
    return [ConnectionResponse.model_validate(c) for c in connections]


@router.post("/connections/sync")
async def sync_connections(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync LinkedIn connections (requires OAuth)"""
    if not current_user.linkedin_access_token:
        raise HTTPException(
            status_code=400, 
            detail="LinkedIn not connected. Please authorize LinkedIn access first."
        )
    
    # background_tasks.add_task(linkedin_service.sync_connections, current_user.id)
    
    return {"message": "Connection sync started", "status": "pending"}


# Referral endpoints
@router.get("", response_model=List[ReferralResponse])
async def list_referrals(
    status: Optional[str] = None,
    company: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List referral requests"""
    query = select(Referral).where(Referral.user_id == current_user.id)
    
    if status:
        query = query.where(Referral.status == status)
    if company:
        query = query.where(Referral.target_company.ilike(f"%{company}%"))
    
    query = query.order_by(Referral.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    referrals = result.scalars().all()
    
    return [ReferralResponse.model_validate(r) for r in referrals]


@router.post("", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referral_data: ReferralCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a referral request"""
    referral = Referral(
        user_id=current_user.id,
        **referral_data.model_dump()
    )
    db.add(referral)
    await db.commit()
    await db.refresh(referral)
    
    return ReferralResponse.model_validate(referral)


@router.post("/{referral_id}/draft", response_model=ReferralResponse)
async def generate_referral_message(
    referral_id: int,
    request: ReferralMessageDraft,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate personalized referral message using AI"""
    result = await db.execute(
        select(Referral)
        .where(Referral.id == referral_id, Referral.user_id == current_user.id)
    )
    referral = result.scalar_one_or_none()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    # This would call the AI service to generate personalized message
    # message = await ai_engine.generate_referral_message(referral, request)
    
    # Placeholder message
    referral.message_draft = f"""Hi {referral.connection_name or 'there'},

I hope this message finds you well. I noticed you're working at {referral.target_company} and I'm very interested in the {referral.target_job_title or 'opportunity'} position.

I would really appreciate it if you could refer me for this role. I believe my background would be a great fit.

Thank you for your time!"""
    
    await db.commit()
    await db.refresh(referral)
    
    return ReferralResponse.model_validate(referral)


@router.post("/{referral_id}/send", response_model=ReferralResponse)
async def send_referral_request(
    referral_id: int,
    request: ReferralSend,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send the referral request message"""
    result = await db.execute(
        select(Referral)
        .where(Referral.id == referral_id, Referral.user_id == current_user.id)
    )
    referral = result.scalar_one_or_none()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    referral.message_sent = request.message
    referral.sent_at = datetime.utcnow()
    referral.status = ReferralStatus.PENDING.value
    
    await db.commit()
    await db.refresh(referral)
    
    # Queue actual message sending
    # if request.via == "linkedin":
    #     background_tasks.add_task(linkedin_service.send_message, referral.id)
    # else:
    #     background_tasks.add_task(email_service.send_referral_email, referral.id)
    
    return ReferralResponse.model_validate(referral)


@router.put("/{referral_id}", response_model=ReferralResponse)
async def update_referral(
    referral_id: int,
    referral_data: ReferralUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update referral status/details"""
    result = await db.execute(
        select(Referral)
        .where(Referral.id == referral_id, Referral.user_id == current_user.id)
    )
    referral = result.scalar_one_or_none()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    update_data = referral_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(referral, field, value)
    
    await db.commit()
    await db.refresh(referral)
    
    return ReferralResponse.model_validate(referral)
