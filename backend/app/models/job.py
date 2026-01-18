"""
Job Model - Discovered Job Listings
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class JobStatus(str, enum.Enum):
    """Job status in user's pipeline"""
    DISCOVERED = "discovered"
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class JobSource(str, enum.Enum):
    """Source of the job posting"""
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    COMPANY_CAREER = "company_career"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    REFERRAL = "referral"
    OTHER = "other"


class Job(Base):
    """Discovered job listings"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Job Details
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    
    # Location
    location = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True)
    is_remote = Column(Boolean, default=False)
    work_type = Column(String(20), nullable=True)  # remote, hybrid, onsite
    
    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(3), default="USD")
    
    # Employment
    employment_type = Column(String(50), nullable=True)  # full-time, part-time, contract
    experience_required = Column(String(50), nullable=True)  # e.g., "3-5 years"
    experience_min_years = Column(Float, nullable=True)
    experience_max_years = Column(Float, nullable=True)
    
    # Source & Links
    source = Column(String(50), default=JobSource.OTHER.value)
    source_url = Column(Text, nullable=True)
    apply_url = Column(Text, nullable=True)
    company_url = Column(String(255), nullable=True)
    
    # AI Analysis
    required_skills = Column(JSON, default=list)  # Extracted skills
    nice_to_have_skills = Column(JSON, default=list)
    education_requirement = Column(String(255), nullable=True)
    
    # Scoring (AI-computed)
    relevance_score = Column(Float, default=0.0)  # 0-1 match score
    skill_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    location_match_score = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), default=JobStatus.DISCOVERED.value)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, nullable=True)
    
    # Dates
    posted_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Raw data for debugging
    raw_data = Column(JSON, nullable=True)
    
    # Relationships
    applications = relationship("Application", back_populates="job")
    
    def __repr__(self):
        return f"<Job {self.title} at {self.company}>"
