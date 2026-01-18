"""
Referral Model - LinkedIn Referral Tracking
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ReferralStatus(str, enum.Enum):
    """Referral request status"""
    DRAFT = "draft"
    PENDING = "pending"  # Message sent, awaiting response
    ACCEPTED = "accepted"
    IGNORED = "ignored"
    DECLINED = "declined"
    REFERRED = "referred"  # Referral submitted
    FOLLOW_UP = "follow_up"  # Need to follow up


class Referral(Base):
    """Referral request tracking"""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    connection_id = Column(Integer, ForeignKey("connections.id", ondelete="SET NULL"), nullable=True)
    
    # Target Details
    target_company = Column(String(255), nullable=False)
    target_job_title = Column(String(255), nullable=True)
    target_job_url = Column(Text, nullable=True)
    
    # Connection Details (cached)
    connection_name = Column(String(255), nullable=True)
    connection_title = Column(String(255), nullable=True)
    connection_linkedin_url = Column(Text, nullable=True)
    connection_email = Column(String(255), nullable=True)
    
    # Message
    message_draft = Column(Text, nullable=True)
    message_sent = Column(Text, nullable=True)
    message_personalization = Column(JSON, nullable=True)  # AI-generated personalization notes
    
    # Status
    status = Column(String(20), default=ReferralStatus.DRAFT.value)
    
    # Timeline
    drafted_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    response_at = Column(DateTime, nullable=True)
    
    # Follow-up
    follow_up_count = Column(Integer, default=0)
    last_follow_up_at = Column(DateTime, nullable=True)
    next_follow_up_at = Column(DateTime, nullable=True)
    
    # Response
    response_message = Column(Text, nullable=True)
    referral_link = Column(Text, nullable=True)  # If they shared an internal referral link
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="referrals")
    connection = relationship("Connection", back_populates="referrals")
    
    def __repr__(self):
        return f"<Referral to {self.connection_name} at {self.target_company}>"


class Connection(Base):
    """LinkedIn connections cache"""
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # LinkedIn Profile
    linkedin_id = Column(String(100), nullable=True, index=True)
    linkedin_url = Column(Text, nullable=True)
    
    # Contact Info
    name = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Professional Info
    headline = Column(String(255), nullable=True)
    current_company = Column(String(255), nullable=True, index=True)
    current_title = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Relationship
    connection_degree = Column(Integer, default=1)  # 1st, 2nd, 3rd
    connected_since = Column(DateTime, nullable=True)
    
    # Categorization
    is_recruiter = Column(Boolean, default=False)
    is_hiring_manager = Column(Boolean, default=False)
    industry = Column(String(100), nullable=True)
    
    # Timestamps
    synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrals = relationship("Referral", back_populates="connection")
    
    def __repr__(self):
        return f"<Connection {self.name} at {self.current_company}>"
