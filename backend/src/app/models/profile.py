"""
Profile Model - User Career Profile with Job Location Preferences
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.core.database import Base


class Profile(Base):
    """User career profile with job preferences"""
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)
    
    # Professional Summary
    headline = Column(String(255), nullable=True)  # e.g., "Senior Software Engineer"
    summary = Column(Text, nullable=True)
    
    # Job Location Preferences (Key Feature)
    preferred_job_countries = Column(JSON, default=list)  # ["India", "USA", "UK"]
    preferred_job_cities = Column(JSON, default=list)  # ["Bangalore", "Mumbai", "Remote"]
    work_authorization = Column(JSON, default=dict)  # {"USA": "H1B", "India": "Citizen"}
    relocation_willing = Column(Boolean, default=False)
    remote_preference = Column(String(20), default="any")  # remote, hybrid, onsite, any
    
    # Experience & Salary
    years_of_experience = Column(Float, default=0)
    current_company = Column(String(255), nullable=True)
    current_title = Column(String(255), nullable=True)
    min_salary_expectation = Column(Integer, nullable=True)  # In USD
    preferred_currency = Column(String(3), default="USD")
    
    # Availability
    notice_period_days = Column(Integer, default=0)
    available_from = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Profile {self.first_name} {self.last_name}>"


class Skill(Base):
    """User skills"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # e.g., "Programming", "Framework", "Tool"
    proficiency = Column(String(20), default="intermediate")  # beginner, intermediate, advanced, expert
    years_used = Column(Float, nullable=True)
    
    profile = relationship("Profile", back_populates="skills")
    
    def __repr__(self):
        return f"<Skill {self.name}>"


class Education(Base):
    """User education history"""
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(100), nullable=False)  # e.g., "Bachelor of Technology"
    field_of_study = Column(String(100), nullable=True)  # e.g., "Computer Science"
    grade = Column(String(20), nullable=True)  # e.g., "8.5 CGPA"
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    
    profile = relationship("Profile", back_populates="education")
    
    def __repr__(self):
        return f"<Education {self.degree} at {self.institution}>"


class Experience(Base):
    """User work experience"""
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    
    company = Column(String(255), nullable=False)
    title = Column(String(100), nullable=False)
    location = Column(String(100), nullable=True)
    employment_type = Column(String(50), nullable=True)  # full-time, part-time, contract, internship
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)  # ["Python", "React", "AWS"]
    
    profile = relationship("Profile", back_populates="experience")
    
    def __repr__(self):
        return f"<Experience {self.title} at {self.company}>"
