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


@router.post("/ai/build")
async def ai_build_resume(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Build a complete resume using AI from user input"""
    from app.agents.ai_engine import ai_engine
    
    try:
        user_input = request.get("userInput", {})
        
        if not user_input:
            raise HTTPException(status_code=400, detail="No user input provided")
        
        # Call AI to build resume
        resume_data = await ai_engine.build_complete_resume(user_input)
        
        if not resume_data or not resume_data.get("personalInfo"):
            raise HTTPException(status_code=500, detail="AI failed to generate resume. Please try again.")
        
        return {"success": True, "resume": resume_data}
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI build resume error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/ai/summary")
async def ai_generate_summary(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Generate a professional summary using AI"""
    from app.agents.ai_engine import ai_engine
    
    user_info = request.get("userInfo", {})
    target_role = request.get("targetRole")
    
    summary = await ai_engine.generate_professional_summary(user_info, target_role)
    
    return {"success": True, "summary": summary}


@router.post("/ai/enhance")
async def ai_enhance_experience(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Enhance job experience description using AI"""
    from app.agents.ai_engine import ai_engine
    
    job_title = request.get("jobTitle", "")
    company = request.get("company", "")
    description = request.get("description", "")
    industry = request.get("industry")
    
    enhanced = await ai_engine.enhance_experience_description(
        job_title, company, description, industry
    )
    
    return {"success": True, "enhanced": enhanced}


@router.post("/ai/skills")
async def ai_suggest_skills(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Get AI-suggested skills for a job role"""
    from app.agents.ai_engine import ai_engine
    
    job_title = request.get("jobTitle", "Software Engineer")
    industry = request.get("industry")
    existing_skills = request.get("existingSkills", [])
    
    suggestions = await ai_engine.suggest_skills(job_title, industry, existing_skills)
    
    return {"success": True, "suggestions": suggestions}


@router.post("/ai/chat")
async def ai_resume_chat(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """AI Chatbot for resume assistance"""
    from app.agents.ai_engine import ai_engine
    
    try:
        message = request.get("message", "")
        resume_context = request.get("resumeContext", {})
        chat_history = request.get("chatHistory", [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        response = await ai_engine.resume_chat(message, resume_context, chat_history)
        
        return {"success": True, **response}
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI chat error: {e}")
        # Return a graceful fallback response instead of 500
        return {
            "success": True,
            "response": "I'm having trouble processing your request right now. Please try again.",
            "suggestions": [],
            "action": "none"
        }



@router.post("/ai/ats-optimize")
async def ai_ats_optimize(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Get ATS optimization suggestions"""
    from app.agents.ai_engine import ai_engine
    
    resume_data = request.get("resumeData", {})
    job_description = request.get("jobDescription")
    
    result = await ai_engine.ats_optimize(resume_data, job_description)
    
    return {"success": True, **result}


@router.post("/ai/projects")
async def ai_suggest_projects(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated project suggestions"""
    from app.agents.ai_engine import ai_engine
    
    skills = request.get("skills", [])
    experience_level = request.get("experienceLevel", "mid")
    industry = request.get("industry")
    
    projects = await ai_engine.generate_projects(skills, experience_level, industry)
    
    return {"success": True, "projects": projects}


@router.post("/ai/certifications")
async def ai_suggest_certifications(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Get certification suggestions"""
    from app.agents.ai_engine import ai_engine
    
    skills = request.get("skills", [])
    target_role = request.get("targetRole", "Software Engineer")
    industry = request.get("industry")
    
    certifications = await ai_engine.suggest_certifications(skills, target_role, industry)
    
    return {"success": True, "certifications": certifications}


@router.post("/ai/achievements")
async def ai_generate_achievements(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated achievement suggestions"""
    from app.agents.ai_engine import ai_engine
    
    role = request.get("role", "Software Engineer")
    industry = request.get("industry", "Technology")
    skills = request.get("skills", [])
    
    achievements = await ai_engine.generate_achievements(role, industry, skills)
    
    return {"success": True, "achievements": achievements}

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
    
    # Normalize text - handle various line endings and extra whitespace
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    full_text = text
    
    # =====================
    # EXTRACT PERSONAL INFO
    # =====================
    
    # Name is usually the first non-email, non-phone, substantial line
    name = ""
    for line in lines[:8]:
        # Skip if it looks like an email, phone, or URL
        if '@' in line or re.search(r'\d{5,}', line) or 'linkedin' in line.lower() or 'github' in line.lower():
            continue
        # Skip common headers
        if line.lower() in ['resume', 'curriculum vitae', 'cv', 'personal details', 'contact']:
            continue
        if len(line) > 2 and len(line) < 60:
            name = line
            break
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    email = email_match.group(0) if email_match else ""
    
    # Extract phone - IMPROVED for Indian formats
    phone_patterns = [
        r'\+91[\s\-]?\d{5}[\s\-]?\d{5}',  # +91 98765 43210
        r'\+91[\s\-]?\d{10}',              # +91 9876543210
        r'91[\s\-]?\d{10}',                # 91 9876543210
        r'\d{5}[\s\-]?\d{5}',              # 98765 43210 (Indian mobile)
        r'\d{10}',                          # 9876543210
        r'\+\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',  # International
        r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',  # US format
    ]
    phone = ""
    for pattern in phone_patterns:
        match = re.search(pattern, full_text)
        if match:
            phone = match.group(0).strip()
            # Validate it's not too long (could be other numbers)
            if len(re.sub(r'\D', '', phone)) <= 13:
                break
    
    # Extract location - IMPROVED for Indian cities
    location = ""
    indian_cities = ['Hyderabad', 'Mumbai', 'Bangalore', 'Bengaluru', 'Delhi', 'Chennai', 'Kolkata', 
                     'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 
                     'Thane', 'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad',
                     'Noida', 'Gurgaon', 'Gurugram', 'Bhilai', 'Raipur']
    indian_states = ['Telangana', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Andhra Pradesh',
                     'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Madhya Pradesh', 'Chhattisgarh',
                     'West Bengal', 'Kerala', 'Punjab', 'Haryana', 'Bihar', 'Odisha']
    
    for city in indian_cities:
        if city.lower() in full_text.lower():
            location = city
            # Try to find state
            for state in indian_states:
                if state.lower() in full_text.lower():
                    location = f"{city}, {state}"
                    break
            break
    
    # Fallback to regex patterns
    if not location:
        location_patterns = [
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z][a-z]+)',
            r'([A-Z][a-z]+),\s*([A-Z]{2})\b',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, full_text[:800])
            if match:
                location = match.group(0)
                break
    
    # Extract LinkedIn
    linkedin = ""
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', full_text, re.IGNORECASE)
    if linkedin_match:
        linkedin = f"https://{linkedin_match.group(0)}"
    
    # GitHub
    github = ""
    github_match = re.search(r'github\.com/[\w-]+', full_text, re.IGNORECASE)
    if github_match:
        github = f"https://{github_match.group(0)}"
    
    # =====================
    # IDENTIFY SECTIONS - IMPROVED headers
    # =====================
    
    section_headers = {
        'summary': ['summary', 'professional summary', 'career summary', 'profile', 'objective', 
                    'career objective', 'about me', 'about', 'introduction', 'overview'],
        'experience': ['experience', 'work experience', 'professional experience', 'employment', 
                       'work history', 'career history', 'employment history', 'internship', 
                       'internships', 'work', 'professional background'],
        'education': ['education', 'academic', 'qualifications', 'academic background', 
                      'educational qualification', 'educational qualifications', 'academics'],
        'skills': ['skills', 'technical skills', 'core competencies', 'competencies', 
                   'technologies', 'tech stack', 'expertise', 'proficiencies', 'key skills',
                   'technical expertise', 'programming languages', 'languages and tools'],
        'projects': ['projects', 'key projects', 'personal projects', 'academic projects', 
                     'major projects', 'project work'],
        'certifications': ['certifications', 'certificates', 'licenses', 'courses', 
                           'training', 'achievements', 'awards']
    }
    
    def find_section_indices(lines, headers):
        """Find start and end indices of each section"""
        sections = {}
        for i, line in enumerate(lines):
            lower_line = line.lower().strip()
            # Remove common punctuation and formatting
            lower_line = re.sub(r'^[#\*\-_•●○▪\s]+', '', lower_line)
            lower_line = re.sub(r'[:\-_|#\*]+$', '', lower_line).strip()
            
            for section_name, patterns in headers.items():
                for pattern in patterns:
                    # Match if line is exactly the pattern or starts with it
                    if lower_line == pattern or lower_line == pattern + 's':
                        if section_name not in sections:
                            sections[section_name] = {'start': i, 'end': len(lines)}
                        break
        
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
        summary_lines = lines[start+1:min(start+8, end)]
        summary = ' '.join(summary_lines)
    
    # =====================
    # EXTRACT EXPERIENCE - IMPROVED
    # =====================
    
    experiences = []
    if 'experience' in section_indices:
        start, end = section_indices['experience']
        exp_lines = lines[start+1:end]
        
        current_exp = None
        
        # Date patterns - multiple formats
        date_patterns = [
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\'?\d{2,4})\s*[-–—to]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\'?\d{2,4}|Present|Current|Till Date|Ongoing)',
            r'((?:19|20)\d{2})\s*[-–—to]+\s*((?:19|20)\d{2}|Present|Current|Till Date|Ongoing)',
            r'(\d{1,2}/\d{2,4})\s*[-–—to]+\s*(\d{1,2}/\d{2,4}|Present|Current)',
        ]
        
        for idx, line in enumerate(exp_lines):
            # Check if this line contains dates
            date_match = None
            for pattern in date_patterns:
                date_match = re.search(pattern, line, re.IGNORECASE)
                if date_match:
                    break
            
            # Check if this looks like a job title or company line
            looks_like_title = (
                len(line) > 5 and 
                not line.startswith(('•', '-', '●', '*', '○', '▪', '→', '►')) and
                (any(c.isupper() for c in line[:5]) or date_match)
            )
            
            # Job title keywords
            title_keywords = ['developer', 'engineer', 'manager', 'analyst', 'designer', 
                             'intern', 'associate', 'consultant', 'lead', 'senior', 
                             'junior', 'trainee', 'executive', 'specialist', 'coordinator']
            has_title_keyword = any(kw in line.lower() for kw in title_keywords)
            
            if looks_like_title and (date_match or has_title_keyword):
                # Save previous experience
                if current_exp and (current_exp['position'] or current_exp['company']):
                    experiences.append(current_exp)
                
                # Parse dates
                start_date = date_match.group(1) if date_match else ""
                end_date = date_match.group(2) if date_match else ""
                is_current = any(kw in end_date.lower() for kw in ['present', 'current', 'till date', 'ongoing']) if end_date else False
                
                # Extract title and company
                line_clean = line
                if date_match:
                    line_clean = line[:date_match.start()].strip()
                
                # Try to split by common separators
                parts = re.split(r'\s*[-–—|@]\s*|\s+at\s+|\s+in\s+', line_clean, maxsplit=1)
                
                position = parts[0].strip() if parts else ""
                company = parts[1].strip() if len(parts) > 1 else ""
                
                # If no company, check next line
                if not company and idx + 1 < len(exp_lines):
                    next_line = exp_lines[idx + 1]
                    if not next_line.startswith(('•', '-', '●', '*', '○')) and len(next_line) < 80:
                        company = next_line
                
                current_exp = {
                    'position': position,
                    'company': company,
                    'startDate': start_date,
                    'endDate': "" if is_current else end_date,
                    'current': is_current,
                    'description': '',
                    'highlights': []
                }
            elif current_exp and line.startswith(('•', '-', '●', '*', '○', '▪', '→', '►')):
                # This is a bullet point
                highlight = re.sub(r'^[•\-●*○▪→►]\s*', '', line).strip()
                if highlight and len(highlight) > 5:
                    current_exp['highlights'].append(highlight)
            elif current_exp and line and len(current_exp['highlights']) == 0:
                # Could be description or company name
                if not current_exp['company'] and len(line) < 80:
                    current_exp['company'] = line
                else:
                    current_exp['description'] += ' ' + line
        
        # Add last experience
        if current_exp and (current_exp['position'] or current_exp['company']):
            current_exp['description'] = current_exp['description'].strip()
            experiences.append(current_exp)
    
    # =====================
    # FALLBACK: Try to find experience even without section header
    # =====================
    if not experiences:
        # Look for job titles anywhere in the document
        job_title_pattern = r'((?:Senior|Junior|Lead|Sr\.?|Jr\.?)?\s*(?:Software|Web|Full[\s-]?Stack|Frontend|Backend|Data|ML|AI|DevOps|Cloud|Mobile|QA|Test)?\s*(?:Developer|Engineer|Analyst|Designer|Architect|Intern|Trainee))[\s\-–—@|]+([A-Za-z\s&]+?)(?:\s*[-–—|]\s*|\s*\(?\s*)((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\'?\d{2,4}|(?:19|20)\d{2})'
        
        for match in re.finditer(job_title_pattern, full_text, re.IGNORECASE):
            experiences.append({
                'position': match.group(1).strip(),
                'company': match.group(2).strip(),
                'startDate': match.group(3),
                'endDate': '',
                'current': False,
                'description': '',
                'highlights': []
            })
    
    # =====================
    # EXTRACT EDUCATION
    # =====================
    
    education = []
    if 'education' in section_indices:
        start, end = section_indices['education']
        edu_lines = lines[start+1:end]
        
        degree_patterns = [
            r"(Bachelor'?s?|Master'?s?|Ph\.?D\.?|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?|B\.?Tech\.?|M\.?Tech\.?|MBA|MCA|BCA|B\.?Com\.?|M\.?Com\.?|B\.?Sc\.?|M\.?Sc\.?|Diploma|Associate'?s?|XII|12th|X|10th|HSC|SSC|CBSE|ICSE|Intermediate)",
        ]
        
        current_edu = None
        
        for line in edu_lines:
            # Check for degree patterns
            has_degree = any(re.search(p, line, re.IGNORECASE) for p in degree_patterns)
            
            # Check for year pattern
            year_matches = re.findall(r'(19|20)\d{2}', line)
            
            if has_degree or (year_matches and not current_edu):
                if current_edu:
                    education.append(current_edu)
                
                # Try to parse institution and degree
                degree_match = re.search(degree_patterns[0], line, re.IGNORECASE)
                degree = degree_match.group(0) if degree_match else ""
                
                # Extract years
                start_year = year_matches[0] + year_matches[0][-2:] if year_matches else ""
                end_year = year_matches[1] + year_matches[1][-2:] if len(year_matches) > 1 else (year_matches[0] + year_matches[0][-2:] if year_matches else "")
                
                # Try to keep years as full 4 digits
                start_year = year_matches[0] if year_matches else ""
                end_year = year_matches[1] if len(year_matches) > 1 else year_matches[0] if year_matches else ""
                
                # Get institution (remove degree and dates)
                institution = line
                if degree_match:
                    institution = institution.replace(degree_match.group(0), '')
                for year in year_matches:
                    institution = institution.replace(year, '')
                institution = re.sub(r'[-–—,|:\s]+', ' ', institution).strip()
                
                current_edu = {
                    'institution': institution[:150],
                    'degree': degree,
                    'field': '',
                    'startDate': start_year,
                    'endDate': end_year
                }
            elif current_edu and line and not line.startswith(('•', '-', '●')):
                # Might be field of study or additional info
                if not current_edu['field'] and len(line) < 100:
                    current_edu['field'] = line[:100]
        
        if current_edu:
            education.append(current_edu)
    
    # =====================
    # EXTRACT SKILLS
    # =====================
    
    skills = []
    if 'skills' in section_indices:
        start, end = section_indices['skills']
        skill_lines = lines[start+1:min(end, start+20)]
        
        for line in skill_lines:
            # Split by common delimiters
            line_skills = re.split(r'[,;•|●○▪\t:]+', line)
            for skill in line_skills:
                skill = skill.strip()
                # Filter out non-skills and clean up
                skill = re.sub(r'^[-\s•●○▪]+', '', skill).strip()
                if skill and len(skill) > 1 and len(skill) < 50:
                    # Exclude common non-skill words
                    if skill.lower() not in ['and', 'or', 'the', 'etc', 'others']:
                        skills.append(skill)
    
    # Deduplicate skills preserving order
    seen = set()
    unique_skills = []
    for s in skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique_skills.append(s)
    skills = unique_skills[:30]
    
    # =====================
    # EXTRACT PROJECTS
    # =====================
    
    projects = []
    if 'projects' in section_indices:
        start, end = section_indices['projects']
        proj_lines = lines[start+1:end]
        
        current_proj = None
        for line in proj_lines:
            if not line.startswith(('•', '-', '●', '*', '○')) and len(line) > 3:
                if current_proj:
                    projects.append(current_proj)
                current_proj = {
                    'name': line[:100],
                    'description': '',
                    'technologies': []
                }
            elif current_proj and line.startswith(('•', '-', '●', '*', '○')):
                desc = re.sub(r'^[•\-●*○]\s*', '', line).strip()
                current_proj['description'] += ' ' + desc
        
        if current_proj:
            current_proj['description'] = current_proj['description'].strip()
            projects.append(current_proj)
    
    return {
        "personalInfo": {
            "fullName": name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "github": github,
            "summary": summary[:500] if summary else ""
        },
        "summary": summary[:1000] if summary else "",
        "experiences": experiences[:10],
        "education": education[:6],
        "skills": skills,
        "projects": projects[:8],
        "raw_text": full_text[:10000]
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
    template: str = "professional",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download resume as PDF or DOCX with optional template selection"""
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
    
    # Use template from resume if not specified in query
    template_id = template or getattr(resume, 'template', 'professional') or 'professional'
    
    if format.lower() == "docx":
        try:
            file_bytes = resume_builder.generate_docx(content, theme_color, template_id)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{resume.name}.docx"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")
    else:
        # Default to PDF
        try:
            file_bytes = resume_builder.generate_pdf(content, theme_color, template_id)
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
