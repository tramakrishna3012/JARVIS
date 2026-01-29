"""
Referral Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ConnectionBase(BaseModel):
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    headline: Optional[str] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    location: Optional[str] = None
    is_recruiter: bool = False
    is_hiring_manager: bool = False


class ConnectionCreate(ConnectionBase):
    linkedin_id: Optional[str] = None
    connection_degree: int = 1


class ConnectionResponse(ConnectionBase):
    id: int
    linkedin_id: Optional[str] = None
    connection_degree: int
    synced_at: datetime
    
    class Config:
        from_attributes = True


class ReferralCreate(BaseModel):
    job_id: Optional[int] = None
    connection_id: Optional[int] = None
    target_company: str
    target_job_title: Optional[str] = None
    target_job_url: Optional[str] = None


class ReferralMessageDraft(BaseModel):
    """Request to generate referral message"""
    referral_id: int
    tone: str = "professional"  # professional, casual, formal
    include_resume: bool = True
    custom_notes: Optional[str] = None


class ReferralUpdate(BaseModel):
    status: Optional[str] = None
    message_draft: Optional[str] = None
    notes: Optional[str] = None
    next_follow_up_at: Optional[datetime] = None


class ReferralSend(BaseModel):
    """Request to send referral message"""
    message: str
    via: str = "linkedin"  # linkedin, email


class ReferralResponse(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int] = None
    connection_id: Optional[int] = None
    target_company: str
    target_job_title: Optional[str] = None
    target_job_url: Optional[str] = None
    connection_name: Optional[str] = None
    connection_title: Optional[str] = None
    message_draft: Optional[str] = None
    message_sent: Optional[str] = None
    status: str
    drafted_at: datetime
    sent_at: Optional[datetime] = None
    response_at: Optional[datetime] = None
    follow_up_count: int
    next_follow_up_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class ConnectionSearch(BaseModel):
    """Search for connections at a company"""
    company: str
    include_recruiters: bool = True
    include_hiring_managers: bool = True
    title_keywords: Optional[List[str]] = None
