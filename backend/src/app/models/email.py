"""
Email Model - Email Intelligence Module
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class EmailType(str, enum.Enum):
    """Email type"""
    SENT = "sent"
    RECEIVED = "received"


class EmailStatus(str, enum.Enum):
    """Email status"""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class EmailCategory(str, enum.Enum):
    """Email category"""
    JOB_APPLICATION = "job_application"
    REFERRAL_REQUEST = "referral_request"
    FOLLOW_UP = "follow_up"
    HR_COMMUNICATION = "hr_communication"
    INTERVIEW_SCHEDULING = "interview_scheduling"
    OFFER_NEGOTIATION = "offer_negotiation"
    REJECTION = "rejection"
    OTHER = "other"


class Email(Base):
    """Email tracking"""
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Thread
    thread_id = Column(String(100), nullable=True, index=True)
    in_reply_to_id = Column(Integer, ForeignKey("emails.id", ondelete="SET NULL"), nullable=True)
    
    # Type & Direction
    email_type = Column(String(20), default=EmailType.SENT.value)
    category = Column(String(30), default=EmailCategory.OTHER.value)
    
    # Headers
    message_id = Column(String(255), nullable=True, unique=True)
    from_address = Column(String(255), nullable=False)
    to_addresses = Column(JSON, default=list)  # ["email1", "email2"]
    cc_addresses = Column(JSON, default=list)
    bcc_addresses = Column(JSON, default=list)
    reply_to = Column(String(255), nullable=True)
    
    # Content
    subject = Column(String(500), nullable=False)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    
    # Attachments
    attachments = Column(JSON, default=list)
    # [{"filename": "resume.pdf", "content_type": "application/pdf", "size": 1024, "url": "..."}]
    
    # Related Entities
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    referral_id = Column(Integer, ForeignKey("referrals.id", ondelete="SET NULL"), nullable=True)
    
    # Status
    status = Column(String(20), default=EmailStatus.DRAFT.value)
    
    # Tracking
    opened_at = Column(DateTime, nullable=True)
    open_count = Column(Integer, default=0)
    clicked_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
    
    # AI Analysis
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    intent = Column(String(50), nullable=True)  # e.g., "interview_invitation", "rejection"
    ai_summary = Column(Text, nullable=True)
    action_required = Column(Boolean, default=False)
    suggested_action = Column(Text, nullable=True)
    
    # Error
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emails")
    replies = relationship("Email", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Email {self.subject[:50]}>"
