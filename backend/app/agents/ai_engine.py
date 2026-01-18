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


# Singleton instance
ai_engine = AIEngine()
