"""
Resumes API Routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.schemas.resume import (
    ResumeCreate, ResumeGenerate, ResumeUpdate, ResumeResponse, ATSAnalysis
)


router = APIRouter()


@router.get("", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all resumes for current user"""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id, Resume.is_archived == False)
        .order_by(Resume.updated_at.desc())
    )
    resumes = result.scalars().all()
    
    return [ResumeResponse.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get resume details"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return ResumeResponse.model_validate(resume)


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new resume manually"""
    resume = Resume(
        user_id=current_user.id,
        name=resume_data.name,
        is_master=resume_data.is_master,
        content=resume_data.content.model_dump(),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    return ResumeResponse.model_validate(resume)


@router.post("/generate", response_model=ResumeResponse)
async def generate_resume(
    request: ResumeGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a tailored resume for a job using AI"""
    # Get the target job
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create resume entry
    resume = Resume(
        user_id=current_user.id,
        name=request.name or f"Resume for {job.title} at {job.company}",
        target_job_id=job.id,
        target_job_title=job.title,
        target_company=job.company,
        content={},  # Will be populated by AI service
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    # Queue AI generation in background
    # background_tasks.add_task(resume_builder.generate, resume.id, current_user.id, request)
    
    return ResumeResponse.model_validate(resume)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse an existing resume (PDF or DOCX)"""
    # Validate file type
    allowed_types = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )
    
    # Read file content
    content = await file.read()
    
    # Parse based on file type
    try:
        if file.content_type == 'application/pdf':
            parsed_content = await parse_pdf(content)
        else:
            parsed_content = await parse_docx(content)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse resume: {str(e)}"
        )
    
    # Create resume with parsed content
    resume = Resume(
        user_id=current_user.id,
        name=file.filename or "Uploaded Resume",
        content=parsed_content,
        is_master=False,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    
    return {
        "id": resume.id,
        "name": resume.name,
        "content": parsed_content,
        "message": "Resume parsed successfully"
    }


async def parse_pdf(content: bytes) -> dict:
    """Parse PDF content and extract text"""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        return extract_resume_data(text)
    except ImportError:
        # Fallback if PyMuPDF not installed
        return {
            "personalInfo": {"fullName": ""},
            "summary": "",
            "experiences": [],
            "education": [],
            "skills": [],
            "raw_text": "PDF parsing requires PyMuPDF. Please install it with: pip install pymupdf"
        }


async def parse_docx(content: bytes) -> dict:
    """Parse DOCX content and extract text"""
    try:
        from docx import Document
        import io as iomodule
        
        doc = Document(iomodule.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs])
        
        return extract_resume_data(text)
    except ImportError:
        return {
            "personalInfo": {"fullName": ""},
            "summary": "",
            "experiences": [],
            "education": [],
            "skills": [],
            "raw_text": "DOCX parsing requires python-docx. Please install it."
        }


def extract_resume_data(text: str) -> dict:
    """Extract structured resume data from raw text"""
    import re
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Basic extraction - name is usually the first non-empty line
    name = lines[0] if lines else ""
    
    # Try to find email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""
    
    # Try to find phone
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,}', text)
    phone = phone_match.group(0).strip() if phone_match else ""
    
    # Extract sections based on common headers
    sections = {
        'summary': '',
        'experience': [],
        'education': [],
        'skills': []
    }
    
    # Look for skills (common patterns)
    skills_patterns = ['skills', 'technical skills', 'competencies', 'technologies']
    for i, line in enumerate(lines):
        lower_line = line.lower()
        if any(pattern in lower_line for pattern in skills_patterns):
            # Get the next few lines as skills
            skill_lines = lines[i+1:i+5]
            for skill_line in skill_lines:
                # Split by common delimiters
                skills = re.split(r'[,;•|\t]', skill_line)
                sections['skills'].extend([s.strip() for s in skills if s.strip() and len(s.strip()) < 50])
    
    return {
        "personalInfo": {
            "fullName": name,
            "email": email,
            "phone": phone,
            "location": "",
            "summary": ""
        },
        "summary": "",
        "experiences": [],
        "education": [],
        "skills": sections['skills'][:20],  # Limit to 20 skills
        "raw_text": text[:5000]  # Keep first 5000 chars for reference
    }


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update resume"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    update_data = resume_data.model_dump(exclude_unset=True)
    if 'content' in update_data and update_data['content']:
        update_data['content'] = update_data['content'].model_dump()
    
    for field, value in update_data.items():
        setattr(resume, field, value)
    
    # Increment version on content changes
    if 'content' in update_data:
        resume.version += 1
    
    await db.commit()
    await db.refresh(resume)
    
    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: int,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download resume as PDF or DOCX"""
    from app.services.resume_builder import resume_builder
    
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get resume content
    content = resume.content or {}
    theme_color = getattr(resume, 'theme_color', '#3B82F6') or '#3B82F6'
    
    if format.lower() == "docx":
        try:
            file_bytes = resume_builder.generate_docx(content, theme_color)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{resume.name}.docx"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")
    else:
        # Default to PDF
        try:
            file_bytes = resume_builder.generate_pdf(content, theme_color)
            media_type = "application/pdf"
            filename = f"{resume.name}.pdf"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/{resume_id}/analyze", response_model=ATSAnalysis)
async def analyze_resume_ats(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze resume for ATS compatibility"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # This would call the ATS analysis service
    # analysis = await ats_analyzer.analyze(resume)
    
    return ATSAnalysis(
        score=85,
        issues=["Consider adding more keywords"],
        suggestions=["Add quantifiable achievements"],
        missing_keywords=["kubernetes", "docker"],
        format_issues=[]
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive a resume (soft delete)"""
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume.is_archived = True
    await db.commit()
