"""
Email Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


class EmailAttachment(BaseModel):
    filename: str
    content_type: str
    size: int
    url: Optional[str] = None


class EmailCreate(BaseModel):
    to_addresses: List[EmailStr]
    cc_addresses: List[EmailStr] = []
    bcc_addresses: List[EmailStr] = []
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    category: str = "other"
    job_id: Optional[int] = None
    application_id: Optional[int] = None
    referral_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class EmailSend(BaseModel):
    """Request to send email"""
    to_addresses: List[EmailStr]
    cc_addresses: List[EmailStr] = []
    subject: str
    body: str
    is_html: bool = False
    attachments: List[int] = []  # Resume IDs to attach
    category: str = "other"
    job_id: Optional[int] = None


class EmailReply(BaseModel):
    """Reply to an email"""
    email_id: int
    body: str
    is_html: bool = False


class EmailResponse(BaseModel):
    id: int
    user_id: int
    thread_id: Optional[str] = None
    email_type: str
    category: str
    from_address: str
    to_addresses: List[str]
    cc_addresses: List[str] = []
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[EmailAttachment] = []
    status: str
    sentiment: Optional[str] = None
    intent: Optional[str] = None
    ai_summary: Optional[str] = None
    action_required: bool
    suggested_action: Optional[str] = None
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailThread(BaseModel):
    """Email conversation thread"""
    thread_id: str
    subject: str
    participants: List[str]
    message_count: int
    last_message_at: datetime
    messages: List[EmailResponse]


class EmailStats(BaseModel):
    """Email statistics"""
    total_sent: int
    total_received: int
    pending_replies: int
    action_required: int
    by_category: Dict[str, int]
