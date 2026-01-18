"""
Resume Builder Service - PDF Generation
"""

import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class ResumeBuilder:
    """Service for generating ATS-friendly PDF resumes"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='Name',
            fontSize=18,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            textColor=colors.HexColor('#1a1a1a')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#2563eb')
        ))
        
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceBefore=6,
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='Company',
            fontSize=10,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#4b5563')
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            fontSize=10,
            fontName='Helvetica',
            leftIndent=20,
            spaceBefore=2
        ))
    
    def generate_pdf(self, resume_content: Dict[str, Any]) -> bytes:
        """Generate PDF from resume content"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        
        # Personal Info
        personal = resume_content.get('personal', {})
        name = f"{personal.get('first_name', '')} {personal.get('last_name', '')}"
        story.append(Paragraph(name, self.styles['Name']))
        
        contact_parts = []
        if personal.get('email'):
            contact_parts.append(personal['email'])
        if personal.get('phone'):
            contact_parts.append(personal['phone'])
        if personal.get('linkedin_url'):
            contact_parts.append('LinkedIn')
        
        if contact_parts:
            story.append(Paragraph(' | '.join(contact_parts), self.styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Summary
        summary = resume_content.get('summary')
        if summary:
            story.append(Paragraph('PROFESSIONAL SUMMARY', self.styles['SectionHeader']))
            story.append(Paragraph(summary, self.styles['Normal']))
        
        # Skills
        skills = resume_content.get('skills', [])
        if skills:
            story.append(Paragraph('SKILLS', self.styles['SectionHeader']))
            skills_text = ' • '.join(skills[:15])
            story.append(Paragraph(skills_text, self.styles['Normal']))
        
        # Experience
        experience = resume_content.get('experience', [])
        if experience:
            story.append(Paragraph('EXPERIENCE', self.styles['SectionHeader']))
            for exp in experience[:4]:  # Limit to 4 most recent
                title_company = f"<b>{exp.get('title', '')}</b> at {exp.get('company', '')}"
                story.append(Paragraph(title_company, self.styles['JobTitle']))
                
                duration = exp.get('duration', '')
                if duration:
                    story.append(Paragraph(duration, self.styles['Company']))
                
                achievements = exp.get('achievements', [])
                for achievement in achievements[:3]:
                    story.append(Paragraph(f"• {achievement}", self.styles['BulletPoint']))
        
        # Education
        education = resume_content.get('education', [])
        if education:
            story.append(Paragraph('EDUCATION', self.styles['SectionHeader']))
            for edu in education[:2]:
                edu_text = f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')}"
                story.append(Paragraph(edu_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def analyze_ats_compatibility(self, resume_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resume for ATS compatibility"""
        issues = []
        suggestions = []
        score = 100
        
        # Check for essential sections
        if not resume_content.get('summary'):
            issues.append("Missing professional summary")
            score -= 10
        
        if not resume_content.get('skills'):
            issues.append("Missing skills section")
            score -= 15
        
        if len(resume_content.get('experience', [])) == 0:
            issues.append("No work experience listed")
            score -= 20
        
        if len(resume_content.get('education', [])) == 0:
            suggestions.append("Consider adding education details")
            score -= 5
        
        # Check content quality
        for exp in resume_content.get('experience', []):
            if not exp.get('achievements'):
                suggestions.append(f"Add achievements for {exp.get('company', 'your roles')}")
        
        return {
            "score": max(0, min(100, score)),
            "issues": issues,
            "suggestions": suggestions,
            "format_issues": []
        }


# Singleton
resume_builder = ResumeBuilder()
