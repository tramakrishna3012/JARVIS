"""
Audit Log Model - Activity Tracking
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuditLog(Base):
    """Audit log for tracking all system activities"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)
    # e.g., "job.discovered", "resume.generated", "application.submitted", "email.sent"
    
    entity_type = Column(String(50), nullable=True)  # e.g., "job", "resume", "application"
    entity_id = Column(Integer, nullable=True)
    
    # Context
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    # {"job_title": "...", "company": "...", "score": 0.85}
    
    # Request Info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="success")  # success, failed, pending
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.user_id}>"
