"""
Emails API Routes
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.email import Email, EmailType, EmailStatus
from app.schemas.email import (
    EmailCreate, EmailSend, EmailReply, EmailResponse,
    EmailThread, EmailStats
)


router = APIRouter()


@router.get("", response_model=List[EmailResponse])
async def list_emails(
    email_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List emails"""
    query = select(Email).where(Email.user_id == current_user.id)
    
    if email_type:
        query = query.where(Email.email_type == email_type)
    if category:
        query = query.where(Email.category == category)
    if status:
        query = query.where(Email.status == status)
    
    query = query.order_by(Email.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    emails = result.scalars().all()
    
    return [EmailResponse.model_validate(e) for e in emails]


@router.get("/stats", response_model=EmailStats)
async def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get email statistics"""
    # Count by type
    result = await db.execute(
        select(Email.email_type, func.count(Email.id))
        .where(Email.user_id == current_user.id)
        .group_by(Email.email_type)
    )
    type_counts = dict(result.all())
    
    # Count by category
    result = await db.execute(
        select(Email.category, func.count(Email.id))
        .where(Email.user_id == current_user.id)
        .group_by(Email.category)
    )
    category_counts = dict(result.all())
    
    # Pending replies (received emails without reply)
    result = await db.execute(
        select(func.count(Email.id))
        .where(
            Email.user_id == current_user.id,
            Email.email_type == EmailType.RECEIVED.value,
            Email.status != EmailStatus.REPLIED.value
        )
    )
    pending = result.scalar() or 0
    
    # Action required
    result = await db.execute(
        select(func.count(Email.id))
        .where(
            Email.user_id == current_user.id,
            Email.action_required == True
        )
    )
    action_required = result.scalar() or 0
    
    return EmailStats(
        total_sent=type_counts.get(EmailType.SENT.value, 0),
        total_received=type_counts.get(EmailType.RECEIVED.value, 0),
        pending_replies=pending,
        action_required=action_required,
        by_category=category_counts
    )


@router.get("/inbox", response_model=List[EmailResponse])
async def get_inbox(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get received emails (inbox)"""
    query = (
        select(Email)
        .where(
            Email.user_id == current_user.id,
            Email.email_type == EmailType.RECEIVED.value
        )
        .order_by(Email.received_at.desc())
        .offset(skip).limit(limit)
    )
    
    result = await db.execute(query)
    emails = result.scalars().all()
    
    return [EmailResponse.model_validate(e) for e in emails]


@router.get("/sent", response_model=List[EmailResponse])
async def get_sent(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get sent emails"""
    query = (
        select(Email)
        .where(
            Email.user_id == current_user.id,
            Email.email_type == EmailType.SENT.value
        )
        .order_by(Email.sent_at.desc())
        .offset(skip).limit(limit)
    )
    
    result = await db.execute(query)
    emails = result.scalars().all()
    
    return [EmailResponse.model_validate(e) for e in emails]


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get email details"""
    result = await db.execute(
        select(Email)
        .where(Email.id == email_id, Email.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return EmailResponse.model_validate(email)


@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def send_email(
    email_data: EmailSend,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a new email"""
    from app.core.config import settings
    
    email = Email(
        user_id=current_user.id,
        email_type=EmailType.SENT.value,
        from_address=settings.SMTP_USER,
        to_addresses=email_data.to_addresses,
        cc_addresses=email_data.cc_addresses,
        subject=email_data.subject,
        body_text=email_data.body if not email_data.is_html else None,
        body_html=email_data.body if email_data.is_html else None,
        category=email_data.category,
        job_id=email_data.job_id,
        status=EmailStatus.QUEUED.value,
    )
    db.add(email)
    await db.commit()
    await db.refresh(email)
    
    # Queue email sending
    # background_tasks.add_task(email_service.send, email.id)
    
    return EmailResponse.model_validate(email)


@router.post("/{email_id}/reply", response_model=EmailResponse)
async def reply_to_email(
    email_id: int,
    reply_data: EmailReply,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reply to an email"""
    from app.core.config import settings
    
    # Get original email
    result = await db.execute(
        select(Email)
        .where(Email.id == email_id, Email.user_id == current_user.id)
    )
    original = result.scalar_one_or_none()
    
    if not original:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Create reply
    reply = Email(
        user_id=current_user.id,
        email_type=EmailType.SENT.value,
        thread_id=original.thread_id or str(original.id),
        in_reply_to_id=original.id,
        from_address=settings.SMTP_USER,
        to_addresses=[original.from_address],
        subject=f"Re: {original.subject}",
        body_text=reply_data.body if not reply_data.is_html else None,
        body_html=reply_data.body if reply_data.is_html else None,
        category=original.category,
        job_id=original.job_id,
        status=EmailStatus.QUEUED.value,
    )
    db.add(reply)
    
    # Mark original as replied
    original.status = EmailStatus.REPLIED.value
    
    await db.commit()
    await db.refresh(reply)
    
    # Queue sending
    # background_tasks.add_task(email_service.send, reply.id)
    
    return EmailResponse.model_validate(reply)


@router.post("/sync")
async def sync_emails(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync emails from IMAP server"""
    # background_tasks.add_task(email_service.sync_inbox, current_user.id)
    
    return {"message": "Email sync started", "status": "pending"}


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an email"""
    result = await db.execute(
        select(Email)
        .where(Email.id == email_id, Email.user_id == current_user.id)
    )
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    await db.delete(email)
    await db.commit()
