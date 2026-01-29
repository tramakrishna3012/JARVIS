"""
Application Model - Job Application Tracking
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"  # Submission failed


class ApplicationMethod(str, enum.Enum):
    """How the application was submitted"""
    MANUAL = "manual"
    AUTO_FORM = "auto_form"  # Automated form fill
    EMAIL = "email"
    ATS_PORTAL = "ats_portal"
    LINKEDIN_EASY_APPLY = "linkedin_easy_apply"
    REFERRAL = "referral"


class Application(Base):
    """Job application tracking"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    
    # Application Details
    status = Column(String(30), default=ApplicationStatus.PENDING.value)
    method = Column(String(30), default=ApplicationMethod.MANUAL.value)
    
    # Submission Details
    submitted_at = Column(DateTime, nullable=True)
    confirmation_number = Column(String(100), nullable=True)
    confirmation_email = Column(String(255), nullable=True)
    
    # Cover Letter
    cover_letter = Column(Text, nullable=True)
    cover_letter_generated = Column(Boolean, default=False)
    
    # Screening Questions & Answers
    screening_questions = Column(JSON, default=list)
    # [{"question": "...", "answer": "...", "auto_answered": true}]
    
    # Form Data (for re-submission/debugging)
    form_data = Column(JSON, nullable=True)
    
    # Response Tracking
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime, nullable=True)
    response_content = Column(Text, nullable=True)
    
    # Interview Details
    interview_rounds = Column(JSON, default=list)
    # [{"round": 1, "type": "phone", "date": "...", "feedback": "..."}]
    
    # Offer Details
    offer_salary = Column(Integer, nullable=True)
    offer_details = Column(JSON, nullable=True)
    
    # Error Tracking (for failed submissions)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.id} - {self.status}>"
