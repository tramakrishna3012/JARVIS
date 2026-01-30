"""
AI Decision Engine - LLM Integration for Job Scoring & Content Generation
"""

import json
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings


class AIEngine:
    """AI Decision Engine for intelligent job matching and content generation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def calculate_job_score(
        self, 
        job_data: Dict[str, Any], 
        profile_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate relevance score for a job based on user profile"""
        
        prompt = f"""Analyze the match between this job and candidate profile.

JOB:
- Title: {job_data.get('title')}
- Company: {job_data.get('company')}
- Required Skills: {job_data.get('required_skills', [])}
- Experience Required: {job_data.get('experience_required')}
- Location: {job_data.get('location')}
- Remote: {job_data.get('is_remote')}

CANDIDATE:
- Current Title: {profile_data.get('current_title')}
- Years Experience: {profile_data.get('years_of_experience')}
- Skills: {profile_data.get('skills', [])}
- Preferred Countries: {profile_data.get('preferred_job_countries', [])}
- Remote Preference: {profile_data.get('remote_preference')}

Return a JSON object with these scores (0.0 to 1.0):
- overall_score: Overall job match
- skill_match: How well skills match
- experience_match: Experience level match
- location_match: Location/remote preference match
- reasoning: Brief explanation

Return ONLY valid JSON, no markdown."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "relevance_score": result.get("overall_score", 0.5),
                "skill_match_score": result.get("skill_match", 0.5),
                "experience_match_score": result.get("experience_match", 0.5),
                "location_match_score": result.get("location_match", 0.5),
            }
        except Exception as e:
            print(f"AI scoring error: {e}")
            return {
                "relevance_score": 0.5,
                "skill_match_score": 0.5,
                "experience_match_score": 0.5,
                "location_match_score": 0.5,
            }
    
    async def generate_tailored_resume(
        self,
        profile_data: Dict[str, Any],
        job_data: Dict[str, Any],
        existing_resume: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a tailored resume for a specific job"""
        
        prompt = f"""Create a tailored resume for this job application.

IMPORTANT RULES:
1. Use ONLY the provided candidate information - DO NOT invent or hallucinate any skills, experiences, or achievements
2. Optimize the presentation for ATS systems
3. Highlight relevant skills that match the job requirements
4. Keep it to 1 page worth of content

JOB TARGET:
- Title: {job_data.get('title')}
- Company: {job_data.get('company')}
- Required Skills: {job_data.get('required_skills', [])}
- Description: {job_data.get('description', '')[:500]}

CANDIDATE PROFILE:
{json.dumps(profile_data, indent=2, default=str)}

Return a JSON object with this structure:
{{
    "summary": "Professional summary tailored to this role (2-3 sentences)",
    "highlighted_skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "company": "...",
            "title": "...",
            "duration": "...",
            "achievements": ["achievement1", "achievement2"]
        }}
    ],
    "education": [...],
    "keywords": ["ATS keywords to include"]
}}

Return ONLY valid JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Resume generation error: {e}")
            return existing_resume or profile_data
    
    async def generate_cover_letter(
        self,
        profile_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> str:
        """Generate a personalized cover letter"""
        
        prompt = f"""Write a professional cover letter for this job application.

RULES:
1. Use ONLY the provided candidate information
2. Keep it concise (3-4 paragraphs)
3. Highlight relevant experience and skills
4. Show enthusiasm for the company and role

JOB:
- Title: {job_data.get('title')}
- Company: {job_data.get('company')}
- Description: {job_data.get('description', '')[:500]}

CANDIDATE:
- Name: {profile_data.get('first_name')} {profile_data.get('last_name')}
- Current Role: {profile_data.get('current_title')} at {profile_data.get('current_company')}
- Experience: {profile_data.get('years_of_experience')} years
- Key Skills: {profile_data.get('skills', [])[:10]}

Write the cover letter:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Cover letter generation error: {e}")
            return ""
    
    async def generate_referral_message(
        self,
        profile_data: Dict[str, Any],
        connection_data: Dict[str, Any],
        job_data: Dict[str, Any],
        tone: str = "professional"
    ) -> str:
        """Generate personalized referral request message"""
        
        prompt = f"""Write a {tone} referral request message for LinkedIn.

CONTEXT:
- Candidate: {profile_data.get('first_name')}
- Connection: {connection_data.get('name')} ({connection_data.get('current_title')} at {connection_data.get('current_company')})
- Target Role: {job_data.get('title')} at {job_data.get('company')}

RULES:
1. Keep it brief (3-4 sentences max)
2. Be genuine and not pushy
3. Mention any relevant background
4. Make it easy for them to help

Write the message:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Referral message generation error: {e}")
            return ""
    
    async def answer_screening_question(
        self,
        question: str,
        profile_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> str:
        """Answer a job application screening question"""
        
        prompt = f"""Answer this job application screening question based on the candidate's profile.

QUESTION: {question}

CANDIDATE PROFILE:
{json.dumps(profile_data, indent=2, default=str)}

JOB CONTEXT:
- Title: {job_data.get('title')}
- Company: {job_data.get('company')}

RULES:
1. Answer honestly based on the profile
2. If info is not available, provide a reasonable response
3. Keep it concise
4. Be professional

Answer:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Screening question error: {e}")
            return ""
    
    async def analyze_email(
        self,
        email_content: str,
        subject: str
    ) -> Dict[str, Any]:
        """Analyze an email for intent and suggested actions"""
        
        prompt = f"""Analyze this email from a job search context.

SUBJECT: {subject}
CONTENT: {email_content[:1000]}

Return JSON with:
{{
    "sentiment": "positive" | "neutral" | "negative",
    "intent": "interview_invitation" | "rejection" | "follow_up" | "offer" | "information_request" | "other",
    "summary": "Brief 1-2 sentence summary",
    "action_required": true | false,
    "suggested_action": "What should the candidate do next"
}}

Return ONLY valid JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Email analysis error: {e}")
            return {
                "sentiment": "neutral",
                "intent": "other",
                "summary": "",
                "action_required": False,
                "suggested_action": ""
            }
    
    async def generate_professional_summary(
        self,
        user_info: Dict[str, Any],
        target_role: Optional[str] = None
    ) -> str:
        """Generate a professional summary for resume"""
        
        prompt = f"""Write a compelling professional summary for a resume.

USER INFORMATION:
- Name: {user_info.get('name', 'Professional')}
- Current/Recent Role: {user_info.get('current_role', 'Not specified')}
- Years of Experience: {user_info.get('years_experience', 'Not specified')}
- Key Skills: {user_info.get('skills', [])}
- Industry: {user_info.get('industry', 'Technology')}
- Notable Achievements: {user_info.get('achievements', [])}

TARGET ROLE: {target_role or 'General professional position'}

RULES:
1. Keep it to 2-4 sentences (50-100 words)
2. Start with years of experience and expertise area
3. Highlight key achievements with metrics if available
4. End with career goals aligned to target role
5. Use action words and professional tone
6. Make it ATS-friendly

Write the professional summary:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Summary generation error: {e}")
            return ""
    
    async def enhance_experience_description(
        self,
        job_title: str,
        company: str,
        basic_description: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enhance a job experience with better descriptions and achievements"""
        
        prompt = f"""Enhance this job experience for a professional resume.

JOB DETAILS:
- Title: {job_title}
- Company: {company}
- Industry: {industry or 'Technology'}
- Current Description: {basic_description}

Generate:
1. An improved 1-2 sentence job description
2. 3-4 bullet point achievements (start with action verbs, include metrics where possible)

Return JSON:
{{
    "description": "Improved description of the role",
    "highlights": [
        "Achieved X by implementing Y, resulting in Z% improvement",
        "Led team of N to deliver project ahead of schedule",
        "Developed and maintained..."
    ]
}}

RULES:
- Use strong action verbs (Led, Developed, Implemented, Achieved, etc.)
- Include quantifiable metrics where possible
- Make achievements specific and impactful
- Keep each bullet to 1-2 lines

Return ONLY valid JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=400
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Experience enhancement error: {e}")
            return {
                "description": basic_description,
                "highlights": []
            }
    
    async def suggest_skills(
        self,
        job_title: str,
        industry: Optional[str] = None,
        existing_skills: List[str] = []
    ) -> Dict[str, List[str]]:
        """Suggest relevant skills for a job role"""
        
        prompt = f"""Suggest skills for a {job_title} resume.

CONTEXT:
- Target Role: {job_title}
- Industry: {industry or 'Technology'}
- Existing Skills: {existing_skills}

Return JSON with categorized skill suggestions:
{{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "tools": ["tool1", "tool2", ...],
    "certifications": ["cert1", "cert2", ...]
}}

RULES:
1. Suggest 5-8 skills per category
2. Prioritize in-demand, ATS-friendly skills
3. Don't repeat existing skills
4. Focus on skills relevant to the role

Return ONLY valid JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Skills suggestion error: {e}")
            return {
                "technical_skills": [],
                "soft_skills": [],
                "tools": [],
                "certifications": []
            }
    
    async def build_complete_resume(
        self,
        user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build a complete resume from user input using AI"""
        
        prompt = f"""Create a complete professional resume based on this information.

USER INPUT:
{json.dumps(user_input, indent=2, default=str)}

Generate a complete resume in this JSON format:
{{
    "personalInfo": {{
        "fullName": "Name from input",
        "email": "email@example.com",
        "phone": "+1234567890",
        "location": "City, State",
        "linkedin": "linkedin.com/in/profile",
        "github": "github.com/username",
        "portfolio": "portfolio.com",
        "summary": "Professional summary 2-4 sentences"
    }},
    "experiences": [
        {{
            "id": "1",
            "company": "Company Name",
            "position": "Job Title",
            "location": "City, State",
            "startDate": "2022-01",
            "endDate": "2024-01",
            "current": false,
            "description": "Brief role description",
            "highlights": ["Achievement 1", "Achievement 2", "Achievement 3"]
        }}
    ],
    "education": [
        {{
            "id": "1",
            "institution": "University Name",
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "location": "City, State",
            "startDate": "2016-08",
            "endDate": "2020-05"
        }}
    ],
    "skills": ["Skill1", "Skill2", "Skill3", "Skill4", "Skill5"],
    "certifications": []
}}

RULES:
1. Use ONLY information provided - do not invent details
2. If fields are missing, leave them as empty strings
3. For experiences, create impactful achievement bullets
4. Generate a compelling professional summary
5. Suggest relevant skills based on the role
6. Make it ATS-friendly and professional

Return ONLY valid JSON, no markdown code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Ensure required structure
            if "personalInfo" not in result:
                result["personalInfo"] = {}
            if "experiences" not in result:
                result["experiences"] = []
            if "education" not in result:
                result["education"] = []
            if "skills" not in result:
                result["skills"] = []
            if "certifications" not in result:
                result["certifications"] = []
            
            return result
        except json.JSONDecodeError as je:
            print(f"JSON parse error: {je}")
            print(f"Raw content: {content[:500] if content else 'empty'}")
            return {}
        except Exception as e:
            print(f"Resume build error: {e}")
            return {}
    
    async def resume_chat(
        self,
        message: str,
        resume_context: Dict[str, Any],
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """AI Chatbot for resume assistance - conversational interface"""
        
        history_text = ""
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                history_text += f"{msg['role'].upper()}: {msg['content']}\n"
        
        prompt = f"""You are JARVIS, an AI resume assistant. Help the user improve their resume.

CURRENT RESUME SUMMARY:
- Name: {resume_context.get('name', 'Not set')}
- Current Role: {resume_context.get('current_role', 'Not set')}
- Years Experience: {resume_context.get('years_experience', 'Not set')}
- Skills: {', '.join(resume_context.get('skills', [])[:10])}
- Target Role: {resume_context.get('target_role', 'Not specified')}

CHAT HISTORY:
{history_text}

USER MESSAGE: {message}

Respond helpfully and concisely. If suggesting improvements, be specific.
You can:
1. Suggest ways to improve their resume
2. Help write better descriptions
3. Recommend skills to add
4. Provide career advice
5. Help with ATS optimization

Return JSON format:
{{
    "response": "Your helpful response",
    "suggestions": ["optional list of quick actions"],
    "action": "none|improve_summary|add_skill|improve_experience|suggest_certifications"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            return json.loads(content)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Chat error: {e}")
            print(f"Traceback: {error_trace}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}. Please check the server logs or API key configuration.",
                "suggestions": ["Check API Key", "Retry later"],
                "action": "none"
            }
    
    async def ats_optimize(
        self,
        resume_data: Dict[str, Any],
        job_description: str = None
    ) -> Dict[str, Any]:
        """Optimize resume for ATS (Applicant Tracking Systems)"""
        
        prompt = f"""Analyze this resume for ATS (Applicant Tracking System) optimization.

RESUME DATA:
{json.dumps(resume_data, indent=2, default=str)[:2000]}

JOB DESCRIPTION (if provided):
{job_description or 'Not provided - give general ATS tips'}

Analyze and return JSON:
{{
    "ats_score": 0-100,
    "keyword_suggestions": ["keyword1", "keyword2"],
    "formatting_issues": ["issue1", "issue2"],
    "missing_sections": ["section1"],
    "improvements": [
        {{"section": "summary", "suggestion": "Add more keywords"}},
        {{"section": "experience", "suggestion": "Use action verbs"}}
    ],
    "strengths": ["strength1", "strength2"]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            return json.loads(content.strip())
        except Exception as e:
            print(f"ATS optimize error: {e}")
            return {"ats_score": 0, "improvements": [], "error": str(e)}
    
    async def generate_projects(
        self,
        skills: List[str],
        experience_level: str,
        industry: str = None
    ) -> List[Dict[str, Any]]:
        """Generate project suggestions based on skills"""
        
        prompt = f"""Suggest 3 professional projects for a resume based on these skills.

SKILLS: {', '.join(skills[:15])}
EXPERIENCE LEVEL: {experience_level}
INDUSTRY: {industry or 'Technology'}

Return JSON array with realistic project suggestions:
[
    {{
        "name": "Project Name",
        "description": "2-3 sentence description of what was built",
        "technologies": ["Tech1", "Tech2", "Tech3"],
        "highlights": ["Achievement 1", "Achievement 2"],
        "type": "personal|work|freelance|opensource"
    }}
]"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=600
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            return json.loads(content.strip())
        except Exception as e:
            print(f"Projects generation error: {e}")
            return []
    
    async def suggest_certifications(
        self,
        skills: List[str],
        target_role: str,
        industry: str = None
    ) -> List[Dict[str, Any]]:
        """Suggest relevant certifications based on target role"""
        
        prompt = f"""Suggest relevant certifications for this professional.

TARGET ROLE: {target_role}
CURRENT SKILLS: {', '.join(skills[:10])}
INDUSTRY: {industry or 'Technology'}

Return JSON array of certification suggestions:
[
    {{
        "name": "Certification Name",
        "issuer": "Issuing Organization",
        "relevance": "high|medium",
        "reason": "Why this certification helps",
        "estimated_time": "1-3 months"
    }}
]

Suggest 4-5 real, recognized certifications."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            return json.loads(content.strip())
        except Exception as e:
            print(f"Certification suggestion error: {e}")
            return []
    
    async def generate_achievements(
        self,
        role: str,
        industry: str,
        skills: List[str]
    ) -> List[Dict[str, str]]:
        """Generate achievement suggestions based on role"""
        
        prompt = f"""Generate 5 professional achievement examples for a resume.

ROLE: {role}
INDUSTRY: {industry or 'Technology'}
SKILLS: {', '.join(skills[:8])}

Return JSON array of achievement suggestions that can be customized:
[
    {{
        "title": "Achievement Title",
        "description": "Description with metrics placeholder like X%, Y users, Z reduction",
        "category": "performance|leadership|innovation|cost-saving|growth"
    }}
]

Make them specific, quantifiable, and impressive."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            return json.loads(content.strip())
        except Exception as e:
            print(f"Achievement generation error: {e}")
            return []


# Singleton instance
ai_engine = AIEngine()
