"""
Resume Model - Generated Resume Versions
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship
from app.core.database import Base


class Resume(Base):
    """Generated resume versions"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Resume Info
    name = Column(String(255), nullable=False)  # e.g., "Resume for Google SWE"
    version = Column(Integer, default=1)
    is_master = Column(Boolean, default=False)  # Master template
    
    # Target Job (if tailored)
    target_job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    target_job_title = Column(String(255), nullable=True)
    target_company = Column(String(255), nullable=True)
    
    # Content (structured)
    content = Column(JSON, nullable=False, default=dict)
    # Structure:
    # {
    #   "personal": {...},
    #   "summary": "...",
    #   "experience": [...],
    #   "education": [...],
    #   "skills": [...],
    #   "projects": [...],
    #   "certifications": [...]
    # }
    
    # Generated PDF
    pdf_content = Column(LargeBinary, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    
    # AI Generation Details
    ai_prompt_used = Column(Text, nullable=True)
    ai_model_used = Column(String(50), nullable=True)
    
    # ATS Optimization
    ats_score = Column(Integer, nullable=True)  # 0-100
    ats_feedback = Column(JSON, nullable=True)
    keywords_included = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")
    
    def __repr__(self):
        return f"<Resume {self.name} v{self.version}>"
