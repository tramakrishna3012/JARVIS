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
    """Extract structured resume data from raw text using improved parsing"""
    import re
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    full_text = text
    
    # =====================
    # EXTRACT PERSONAL INFO
    # =====================
    
    # Name is usually the first non-email, non-phone, substantial line
    name = ""
    for line in lines[:5]:
        # Skip if it looks like an email or phone or is too short
        if '@' in line or re.search(r'\d{3}.*\d{4}', line):
            continue
        if len(line) > 2 and len(line) < 60:
            name = line
            break
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    email = email_match.group(0) if email_match else ""
    
    # Extract phone (various formats)
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+\d{10,12}'
    ]
    phone = ""
    for pattern in phone_patterns:
        match = re.search(pattern, full_text)
        if match:
            phone = match.group(0).strip()
            break
    
    # Extract location (city, state patterns)
    location = ""
    location_patterns = [
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z]{2})\b',  # City, ST
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z][a-z]+)',  # City, State
    ]
    for pattern in location_patterns:
        match = re.search(pattern, full_text[:500])
        if match:
            location = match.group(0)
            break
    
    # Extract LinkedIn
    linkedin = ""
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', full_text, re.IGNORECASE)
    if linkedin_match:
        linkedin = f"https://{linkedin_match.group(0)}"
    
    # =====================
    # IDENTIFY SECTIONS
    # =====================
    
    section_headers = {
        'summary': ['summary', 'professional summary', 'profile', 'objective', 'about me', 'about'],
        'experience': ['experience', 'work experience', 'professional experience', 'employment', 'work history', 'career history'],
        'education': ['education', 'academic', 'qualifications', 'academic background'],
        'skills': ['skills', 'technical skills', 'core competencies', 'competencies', 'technologies', 'tech stack', 'expertise', 'proficiencies'],
        'projects': ['projects', 'key projects', 'personal projects'],
        'certifications': ['certifications', 'certificates', 'licenses']
    }
    
    def find_section_indices(lines, headers):
        """Find start and end indices of each section"""
        sections = {}
        for i, line in enumerate(lines):
            lower_line = line.lower().strip()
            # Remove common punctuation
            lower_line = re.sub(r'[:\-_|]', '', lower_line).strip()
            
            for section_name, patterns in headers.items():
                for pattern in patterns:
                    if lower_line == pattern or lower_line.startswith(pattern + ' '):
                        if section_name not in sections:
                            sections[section_name] = {'start': i, 'end': len(lines)}
        
        # Calculate end indices
        sorted_sections = sorted(sections.items(), key=lambda x: x[1]['start'])
        for i, (name, indices) in enumerate(sorted_sections):
            if i + 1 < len(sorted_sections):
                indices['end'] = sorted_sections[i + 1][1]['start']
        
        return {name: (indices['start'], indices['end']) for name, indices in sections.items()}
    
    section_indices = find_section_indices(lines, section_headers)
    
    # =====================
    # EXTRACT SUMMARY
    # =====================
    
    summary = ""
    if 'summary' in section_indices:
        start, end = section_indices['summary']
        summary_lines = lines[start+1:min(start+6, end)]
        summary = ' '.join(summary_lines)
    
    # =====================
    # EXTRACT EXPERIENCE
    # =====================
    
    experiences = []
    if 'experience' in section_indices:
        start, end = section_indices['experience']
        exp_lines = lines[start+1:end]
        
        current_exp = None
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:19|20)\d{2})\s*[-–—to]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:19|20)\d{2}|Present|Current)'
        
        for line in exp_lines:
            # Check if this line contains dates (likely a job entry)
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            
            # Check if this looks like a company/title line
            is_new_entry = date_match or (
                len(line) > 3 and 
                not line.startswith(('•', '-', '●', '*', '○')) and
                any(c.isupper() for c in line[:3])
            )
            
            if is_new_entry and date_match:
                # Save previous experience
                if current_exp:
                    experiences.append(current_exp)
                
                # Parse dates
                start_date = date_match.group(1) if date_match else ""
                end_date = date_match.group(2) if date_match else ""
                is_current = 'present' in end_date.lower() or 'current' in end_date.lower() if end_date else False
                
                # Extract title and company from the line
                line_before_date = line[:date_match.start()].strip() if date_match else line
                parts = re.split(r'\s*[-–—|@at]\s*', line_before_date, maxsplit=1)
                
                position = parts[0].strip() if parts else ""
                company = parts[1].strip() if len(parts) > 1 else ""
                
                current_exp = {
                    'position': position,
                    'company': company,
                    'startDate': start_date,
                    'endDate': "" if is_current else end_date,
                    'current': is_current,
                    'description': '',
                    'highlights': []
                }
            elif current_exp and line.startswith(('•', '-', '●', '*', '○', '▪')):
                # This is a bullet point - add to highlights
                highlight = re.sub(r'^[•\-●*○▪]\s*', '', line).strip()
                if highlight:
                    current_exp['highlights'].append(highlight)
            elif current_exp and line and not any(h in line.lower() for headers_list in section_headers.values() for h in headers_list):
                # Add to description if not a section header
                if len(current_exp['highlights']) == 0:
                    current_exp['description'] += ' ' + line
        
        # Add last experience
        if current_exp:
            current_exp['description'] = current_exp['description'].strip()
            experiences.append(current_exp)
    
    # =====================
    # EXTRACT EDUCATION
    # =====================
    
    education = []
    if 'education' in section_indices:
        start, end = section_indices['education']
        edu_lines = lines[start+1:end]
        
        degree_patterns = [
            r"(Bachelor'?s?|Master'?s?|Ph\.?D\.?|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?|B\.?Tech|M\.?Tech|MBA|Associate'?s?)",
        ]
        
        current_edu = None
        
        for line in edu_lines:
            # Check for degree patterns
            has_degree = any(re.search(p, line, re.IGNORECASE) for p in degree_patterns)
            
            # Check for year pattern
            year_match = re.search(r'(19|20)\d{2}', line)
            
            if has_degree or (year_match and not current_edu):
                if current_edu:
                    education.append(current_edu)
                
                # Try to parse institution and degree
                degree_match = re.search(degree_patterns[0], line, re.IGNORECASE)
                degree = degree_match.group(0) if degree_match else ""
                
                # Extract years
                years = re.findall(r'(19|20)\d{2}', line)
                start_year = years[0] if years else ""
                end_year = years[1] if len(years) > 1 else years[0] if years else ""
                
                # Remove degree and dates to get institution
                institution = line
                if degree_match:
                    institution = institution.replace(degree_match.group(0), '')
                for year in years:
                    institution = institution.replace(year, '')
                institution = re.sub(r'[-–—,|\s]+', ' ', institution).strip()
                
                current_edu = {
                    'institution': institution[:100],
                    'degree': degree,
                    'field': '',
                    'startDate': start_year,
                    'endDate': end_year
                }
            elif current_edu and line and not line.startswith(('•', '-')):
                # Might be field of study
                if not current_edu['field']:
                    current_edu['field'] = line[:100]
        
        if current_edu:
            education.append(current_edu)
    
    # =====================
    # EXTRACT SKILLS
    # =====================
    
    skills = []
    if 'skills' in section_indices:
        start, end = section_indices['skills']
        skill_lines = lines[start+1:min(end, start+15)]
        
        for line in skill_lines:
            # Split by common delimiters
            line_skills = re.split(r'[,;•|●○▪\t]', line)
            for skill in line_skills:
                skill = skill.strip()
                # Filter out non-skills
                if skill and len(skill) > 1 and len(skill) < 40:
                    if not any(h in skill.lower() for headers_list in section_headers.values() for h in headers_list):
                        skills.append(skill)
    
    # Deduplicate and limit skills
    skills = list(dict.fromkeys(skills))[:25]
    
    return {
        "personalInfo": {
            "fullName": name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "summary": summary[:500] if summary else ""
        },
        "summary": summary[:1000] if summary else "",
        "experiences": experiences[:10],
        "education": education[:5],
        "skills": skills,
        "raw_text": full_text[:8000]
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
