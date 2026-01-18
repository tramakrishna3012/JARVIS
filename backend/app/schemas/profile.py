"""
Profile Schemas - User career profile validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


# Skill schemas
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: str = "intermediate"
    years_used: Optional[float] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int
    
    class Config:
        from_attributes = True


# Education schemas
class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    grade: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    description: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: int
    
    class Config:
        from_attributes = True


# Experience schemas
class ExperienceBase(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_current: bool = False
    description: Optional[str] = None
    technologies: List[str] = []


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: int
    
    class Config:
        from_attributes = True


# Profile schemas
class ProfileBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    
    # Job Location Preferences
    preferred_job_countries: List[str] = []
    preferred_job_cities: List[str] = []
    work_authorization: dict = {}
    relocation_willing: bool = False
    remote_preference: str = "any"  # remote, hybrid, onsite, any
    
    # Experience & Salary
    years_of_experience: float = 0
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    min_salary_expectation: Optional[int] = None
    preferred_currency: str = "USD"
    
    # Availability
    notice_period_days: int = 0
    available_from: Optional[datetime] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    preferred_job_countries: Optional[List[str]] = None
    preferred_job_cities: Optional[List[str]] = None
    work_authorization: Optional[dict] = None
    relocation_willing: Optional[bool] = None
    remote_preference: Optional[str] = None
    years_of_experience: Optional[float] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    min_salary_expectation: Optional[int] = None
    preferred_currency: Optional[str] = None
    notice_period_days: Optional[int] = None
    available_from: Optional[datetime] = None


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    skills: List[SkillResponse] = []
    education: List[EducationResponse] = []
    experience: List[ExperienceResponse] = []
    
    class Config:
        from_attributes = True
