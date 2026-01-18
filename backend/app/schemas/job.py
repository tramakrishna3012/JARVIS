"""
Job Schemas - Job listing validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    is_remote: bool = False
    work_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    employment_type: Optional[str] = None
    experience_required: Optional[str] = None
    experience_min_years: Optional[float] = None
    experience_max_years: Optional[float] = None


class JobCreate(JobBase):
    source: str = "other"
    source_url: Optional[str] = None
    apply_url: Optional[str] = None
    company_url: Optional[str] = None
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    education_requirement: Optional[str] = None
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None


class JobUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class JobFilter(BaseModel):
    """Filters for job search"""
    countries: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    is_remote: Optional[bool] = None
    work_type: Optional[str] = None
    min_salary: Optional[int] = None
    employment_types: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    status: Optional[str] = None
    min_relevance_score: Optional[float] = None
    skills: Optional[List[str]] = None
    search_query: Optional[str] = None


class JobResponse(JobBase):
    id: int
    source: str
    source_url: Optional[str] = None
    apply_url: Optional[str] = None
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    relevance_score: float = 0.0
    skill_match_score: float = 0.0
    experience_match_score: float = 0.0
    location_match_score: float = 0.0
    status: str
    is_duplicate: bool
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    discovered_at: datetime
    
    class Config:
        from_attributes = True


class JobDiscoverRequest(BaseModel):
    """Request to trigger job discovery"""
    sources: List[str] = ["linkedin", "naukri"]
    keywords: List[str] = []
    countries: Optional[List[str]] = None
    limit: int = Field(default=50, le=200)


class JobDiscoverResponse(BaseModel):
    """Response from job discovery"""
    jobs_found: int
    jobs_new: int
    jobs_duplicate: int
    status: str
