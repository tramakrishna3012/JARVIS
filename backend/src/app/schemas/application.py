"""
Application Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ScreeningQuestion(BaseModel):
    question: str
    answer: str
    auto_answered: bool = False


class InterviewRound(BaseModel):
    round: int
    type: str  # phone, video, onsite, technical, hr
    date: Optional[datetime] = None
    interviewer: Optional[str] = None
    feedback: Optional[str] = None
    status: str = "scheduled"  # scheduled, completed, cancelled


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_letter: Optional[str] = None
    method: str = "manual"


class ApplicationApply(BaseModel):
    """Request to auto-apply to a job"""
    job_id: int
    resume_id: Optional[int] = None
    generate_cover_letter: bool = False
    auto_answer_questions: bool = True


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    screening_questions: Optional[List[ScreeningQuestion]] = None
    interview_rounds: Optional[List[InterviewRound]] = None
    offer_salary: Optional[int] = None
    offer_details: Optional[Dict[str, Any]] = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: Optional[int] = None
    resume_id: Optional[int] = None
    status: str
    method: str
    submitted_at: Optional[datetime] = None
    confirmation_number: Optional[str] = None
    cover_letter: Optional[str] = None
    screening_questions: List[ScreeningQuestion] = []
    interview_rounds: List[InterviewRound] = []
    response_received: bool
    response_date: Optional[datetime] = None
    offer_salary: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationStats(BaseModel):
    """Application statistics"""
    total: int
    pending: int
    submitted: int
    interviewing: int
    offered: int
    rejected: int
    acceptance_rate: float
