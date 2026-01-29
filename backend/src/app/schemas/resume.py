"""
Resume Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ResumeContent(BaseModel):
    """Structured resume content"""
    personal: Dict[str, Any] = {}
    summary: Optional[str] = None
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    skills: List[str] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []


class ResumeCreate(BaseModel):
    name: str
    is_master: bool = False
    content: ResumeContent


class ResumeGenerate(BaseModel):
    """Request to generate tailored resume"""
    job_id: int
    name: Optional[str] = None
    emphasize_skills: List[str] = []
    include_projects: bool = True
    max_pages: int = 1


class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[ResumeContent] = None
    is_active: Optional[bool] = None


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    name: str
    version: int
    is_master: bool
    target_job_id: Optional[int] = None
    target_job_title: Optional[str] = None
    target_company: Optional[str] = None
    content: Dict[str, Any]
    pdf_url: Optional[str] = None
    ats_score: Optional[int] = None
    ats_feedback: Optional[Dict[str, Any]] = None
    keywords_included: List[str] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ATSAnalysis(BaseModel):
    """ATS compatibility analysis"""
    score: int  # 0-100
    issues: List[str] = []
    suggestions: List[str] = []
    missing_keywords: List[str] = []
    format_issues: List[str] = []
