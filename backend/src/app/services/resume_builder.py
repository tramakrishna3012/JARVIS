"""
Resume Builder Service - PDF and DOCX Generation with Multiple Templates
"""

import io
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, ListFlowable, ListItem

# DOCX imports - optional
try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class ResumeBuilder:
    """Service for generating ATS-friendly PDF and DOCX resumes with multiple templates"""
    
    TEMPLATES = {
        'professional': {
            'name_size': 18,
            'section_size': 12,
            'body_size': 10,
            'name_font': 'Helvetica-Bold',
            'section_style': 'uppercase',
            'use_lines': True,
            'compact': False,
        },
        'modern': {
            'name_size': 20,
            'section_size': 11,
            'body_size': 10,
            'name_font': 'Helvetica-Bold',
            'section_style': 'titlecase',
            'use_lines': False,
            'compact': False,
        },
        'tech': {
            'name_size': 16,
            'section_size': 11,
            'body_size': 9,
            'name_font': 'Helvetica-Bold',
            'section_style': 'uppercase',
            'use_lines': True,
            'compact': True,
        },
        'executive': {
            'name_size': 22,
            'section_size': 12,
            'body_size': 10,
            'name_font': 'Times-Bold',
            'section_style': 'uppercase',
            'use_lines': True,
            'compact': False,
        },
        'creative': {
            'name_size': 24,
            'section_size': 12,
            'body_size': 10,
            'name_font': 'Helvetica-Bold',
            'section_style': 'uppercase',
            'use_lines': False,
            'compact': False,
        },
        'academic': {
            'name_size': 16,
            'section_size': 11,
            'body_size': 10,
            'name_font': 'Times-Bold',
            'section_style': 'titlecase',
            'use_lines': True,
            'compact': False,
        },
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def _setup_template_styles(self, template_id: str, theme_color: str):
        """Setup styles based on selected template"""
        template = self.TEMPLATES.get(template_id, self.TEMPLATES['professional'])
        
        # Clear and recreate custom styles
        custom_styles = ['Name', 'SectionHeader', 'JobTitle', 'Company', 'BulletPoint', 'ContactInfo', 'Skills']
        for style_name in custom_styles:
            if style_name in self.styles.byName:
                del self.styles.byName[style_name]
        
        self.styles.add(ParagraphStyle(
            name='Name',
            fontSize=template['name_size'],
            fontName=template['name_font'],
            spaceAfter=4,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=1 if template_id == 'creative' else 0,  # Center for creative
        ))
        
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            fontSize=9,
            fontName='Helvetica',
            spaceAfter=12,
            textColor=colors.HexColor('#4b5563'),
            alignment=1 if template_id == 'creative' else 0,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=template['section_size'],
            fontName='Helvetica-Bold',
            spaceBefore=14 if not template['compact'] else 10,
            spaceAfter=6 if not template['compact'] else 4,
            textColor=colors.HexColor(theme_color),
        ))
        
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            fontSize=template['body_size'] + 1,
            fontName='Helvetica-Bold',
            spaceBefore=8 if not template['compact'] else 5,
            spaceAfter=2,
            textColor=colors.HexColor('#1f2937'),
        ))
        
        self.styles.add(ParagraphStyle(
            name='Company',
            fontSize=template['body_size'],
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4,
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            fontSize=template['body_size'],
            fontName='Helvetica',
            leftIndent=15,
            spaceBefore=2 if not template['compact'] else 1,
            textColor=colors.HexColor('#374151'),
        ))
        
        self.styles.add(ParagraphStyle(
            name='Skills',
            fontSize=template['body_size'],
            fontName='Helvetica',
            textColor=colors.HexColor('#374151'),
        ))
        
        return template
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if not date_str:
            return ''
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m')
            return date.strftime('%b %Y')
        except:
            return date_str
    
    def _format_section_title(self, title: str, style: str) -> str:
        """Format section title based on template style"""
        if style == 'uppercase':
            return title.upper()
        elif style == 'titlecase':
            return title.title()
        return title
    
    def generate_pdf(self, resume_content: Dict[str, Any], theme_color: str = '#3B82F6', template_id: str = 'professional') -> bytes:
        """Generate PDF from resume content with selected template"""
        buffer = io.BytesIO()
        
        template = self._setup_template_styles(template_id, theme_color)
        
        # Page size and margins
        margins = 0.6 if template['compact'] else 0.75
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=margins*inch,
            leftMargin=margins*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        
        # Personal Info
        personal = resume_content.get('personalInfo', resume_content.get('personal', {}))
        
        # Name
        name = personal.get('fullName') or f"{personal.get('first_name', '')} {personal.get('last_name', '')}".strip()
        if name:
            story.append(Paragraph(name, self.styles['Name']))
        
        # Contact line
        contact_parts = []
        if personal.get('email'):
            contact_parts.append(personal['email'])
        if personal.get('phone'):
            contact_parts.append(personal['phone'])
        if personal.get('location'):
            contact_parts.append(personal['location'])
        
        if contact_parts:
            separator = '  •  ' if template_id in ['creative', 'modern'] else '  |  '
            story.append(Paragraph(separator.join(contact_parts), self.styles['ContactInfo']))
        
        # Social links line
        link_parts = []
        if personal.get('linkedin'):
            linkedin = personal['linkedin']
            if linkedin.startswith('http'):
                linkedin = linkedin.split('linkedin.com/in/')[-1].rstrip('/')
            link_parts.append(f"LinkedIn: {linkedin}")
        if personal.get('github'):
            github = personal['github']
            if github.startswith('http'):
                github = github.split('github.com/')[-1].rstrip('/')
            link_parts.append(f"GitHub: {github}")
        if personal.get('portfolio'):
            portfolio = personal['portfolio']
            if portfolio.startswith('http'):
                portfolio = portfolio.replace('https://', '').replace('http://', '').rstrip('/')
            link_parts.append(f"Portfolio: {portfolio}")
        if personal.get('twitter'):
            twitter = personal['twitter']
            if twitter.startswith('http'):
                twitter = twitter.split('x.com/')[-1].split('twitter.com/')[-1].rstrip('/')
            link_parts.append(f"X: @{twitter}" if not twitter.startswith('@') else f"X: {twitter}")
        
        if link_parts:
            separator = '  •  ' if template_id in ['creative', 'modern'] else '  |  '
            story.append(Paragraph(separator.join(link_parts), self.styles['ContactInfo']))
        
        # Divider line for templates that use lines
        if template['use_lines']:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(theme_color), spaceAfter=8))
        
        # Professional Summary
        summary = personal.get('summary') or resume_content.get('summary')
        if summary:
            title = self._format_section_title('Professional Summary', template['section_style'])
            story.append(Paragraph(title, self.styles['SectionHeader']))
            if template['use_lines']:
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=6))
            story.append(Paragraph(summary, self.styles['Normal']))
        
        # Experience
        experiences = resume_content.get('experiences', resume_content.get('experience', []))
        if experiences:
            title = self._format_section_title('Professional Experience', template['section_style'])
            story.append(Paragraph(title, self.styles['SectionHeader']))
            if template['use_lines']:
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=6))
            
            max_exp = 4 if template['compact'] else 5
            for exp in experiences[:max_exp]:
                position = exp.get('position') or exp.get('title', '')
                company = exp.get('company', '')
                
                # Job title and company
                if company:
                    title_text = f"<b>{position}</b> at {company}"
                else:
                    title_text = f"<b>{position}</b>"
                story.append(Paragraph(title_text, self.styles['JobTitle']))
                
                # Date range
                start = self._format_date(exp.get('startDate', '')) or exp.get('start_date', '')
                end = 'Present' if exp.get('current') else (self._format_date(exp.get('endDate', '')) or exp.get('end_date', ''))
                duration = f"{start} – {end}" if start else exp.get('duration', '')
                if duration:
                    story.append(Paragraph(duration, self.styles['Company']))
                
                # Description
                description = exp.get('description', '')
                if description:
                    story.append(Paragraph(f"• {description}", self.styles['BulletPoint']))
                
                # Highlights/Achievements
                highlights = exp.get('highlights', exp.get('achievements', []))
                max_highlights = 2 if template['compact'] else 3
                for highlight in highlights[:max_highlights]:
                    story.append(Paragraph(f"• {highlight}", self.styles['BulletPoint']))
        
        # Projects (for tech template)
        projects = resume_content.get('projects', [])
        if projects and template_id in ['tech', 'creative']:
            title = self._format_section_title('Projects', template['section_style'])
            story.append(Paragraph(title, self.styles['SectionHeader']))
            if template['use_lines']:
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=6))
            
            for proj in projects[:3]:
                name = proj.get('name', '')
                desc = proj.get('description', '')
                story.append(Paragraph(f"<b>{name}</b>", self.styles['JobTitle']))
                if desc:
                    story.append(Paragraph(desc, self.styles['BulletPoint']))
        
        # Education
        education = resume_content.get('education', [])
        if education:
            title = self._format_section_title('Education', template['section_style'])
            story.append(Paragraph(title, self.styles['SectionHeader']))
            if template['use_lines']:
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=6))
            
            for edu in education[:3]:
                institution = edu.get('institution', '')
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                
                edu_parts = []
                if degree:
                    edu_parts.append(f"<b>{degree}</b>")
                if field:
                    edu_parts.append(f"in {field}")
                if institution:
                    edu_parts.append(f"– {institution}")
                
                if edu_parts:
                    story.append(Paragraph(' '.join(edu_parts), self.styles['Normal']))
                
                # Date range
                start = self._format_date(edu.get('startDate', ''))
                end = self._format_date(edu.get('endDate', ''))
                if start or end:
                    story.append(Paragraph(f"{start} – {end}", self.styles['Company']))
        
        # Skills
        skills = resume_content.get('skills', [])
        if skills:
            title = self._format_section_title('Technical Skills', template['section_style'])
            story.append(Paragraph(title, self.styles['SectionHeader']))
            if template['use_lines']:
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=6))
            
            max_skills = 15 if template['compact'] else 20
            skills_text = '  •  '.join(skills[:max_skills])
            story.append(Paragraph(skills_text, self.styles['Skills']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_docx(self, resume_content: Dict[str, Any], theme_color: str = '#3B82F6', template_id: str = 'professional') -> bytes:
        """Generate DOCX from resume content with selected template"""
        if not DOCX_AVAILABLE:
            raise Exception("python-docx not installed. Cannot generate DOCX.")
        
        template = self.TEMPLATES.get(template_id, self.TEMPLATES['professional'])
        document = Document()
        
        # Set margins
        margin = 0.6 if template['compact'] else 0.75
        for section in document.sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(margin)
            section.right_margin = Inches(margin)
        
        # Theme color
        rgb = self._hex_to_rgb(theme_color)
        theme_rgb = RGBColor(rgb[0], rgb[1], rgb[2])
        
        # Personal Info
        personal = resume_content.get('personalInfo', resume_content.get('personal', {}))
        
        # Name
        name = personal.get('fullName') or f"{personal.get('first_name', '')} {personal.get('last_name', '')}".strip()
        if name:
            name_para = document.add_heading(name, level=0)
            if template_id == 'creative':
                name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in name_para.runs:
                run.font.size = Pt(template['name_size'])
                run.font.color.rgb = RGBColor(26, 26, 26)
        
        # Contact info
        contact_parts = []
        if personal.get('email'):
            contact_parts.append(personal['email'])
        if personal.get('phone'):
            contact_parts.append(personal['phone'])
        if personal.get('location'):
            contact_parts.append(personal['location'])
        if personal.get('linkedin'):
            linkedin = personal['linkedin']
            if linkedin.startswith('http'):
                linkedin = linkedin.split('linkedin.com/in/')[-1].rstrip('/')
            contact_parts.append(f"LinkedIn: {linkedin}")
        
        if contact_parts:
            separator = '  •  ' if template_id in ['creative', 'modern'] else '  |  '
            contact_para = document.add_paragraph(separator.join(contact_parts))
            if template_id == 'creative':
                contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in contact_para.runs:
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(100, 100, 100)
        
        # Summary
        summary = personal.get('summary') or resume_content.get('summary')
        if summary:
            title = self._format_section_title('Professional Summary', template['section_style'])
            heading = document.add_heading(title, level=1)
            for run in heading.runs:
                run.font.color.rgb = theme_rgb
                run.font.size = Pt(template['section_size'])
            para = document.add_paragraph(summary)
            for run in para.runs:
                run.font.size = Pt(template['body_size'])
        
        # Experience
        experiences = resume_content.get('experiences', resume_content.get('experience', []))
        if experiences:
            title = self._format_section_title('Professional Experience', template['section_style'])
            heading = document.add_heading(title, level=1)
            for run in heading.runs:
                run.font.color.rgb = theme_rgb
                run.font.size = Pt(template['section_size'])
            
            max_exp = 4 if template['compact'] else 5
            for exp in experiences[:max_exp]:
                position = exp.get('position') or exp.get('title', '')
                company = exp.get('company', '')
                
                job_para = document.add_paragraph()
                run = job_para.add_run(position)
                run.bold = True
                run.font.size = Pt(template['body_size'] + 1)
                if company:
                    job_para.add_run(f" at {company}")
                
                # Date range
                start = self._format_date(exp.get('startDate', '')) or exp.get('start_date', '')
                end = 'Present' if exp.get('current') else (self._format_date(exp.get('endDate', '')) or exp.get('end_date', ''))
                if start:
                    date_para = document.add_paragraph(f"{start} – {end}")
                    for run in date_para.runs:
                        run.font.size = Pt(9)
                        run.font.color.rgb = RGBColor(100, 100, 100)
                
                # Description and highlights
                description = exp.get('description', '')
                if description:
                    bullet = document.add_paragraph(description, style='List Bullet')
                    for run in bullet.runs:
                        run.font.size = Pt(template['body_size'])
                
                highlights = exp.get('highlights', exp.get('achievements', []))
                max_highlights = 2 if template['compact'] else 3
                for highlight in highlights[:max_highlights]:
                    bullet = document.add_paragraph(highlight, style='List Bullet')
                    for run in bullet.runs:
                        run.font.size = Pt(template['body_size'])
        
        # Education
        education = resume_content.get('education', [])
        if education:
            title = self._format_section_title('Education', template['section_style'])
            heading = document.add_heading(title, level=1)
            for run in heading.runs:
                run.font.color.rgb = theme_rgb
                run.font.size = Pt(template['section_size'])
            
            for edu in education[:3]:
                institution = edu.get('institution', '')
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                
                edu_para = document.add_paragraph()
                if degree:
                    run = edu_para.add_run(degree)
                    run.bold = True
                if field:
                    edu_para.add_run(f" in {field}")
                if institution:
                    edu_para.add_run(f" – {institution}")
        
        # Skills
        skills = resume_content.get('skills', [])
        if skills:
            title = self._format_section_title('Technical Skills', template['section_style'])
            heading = document.add_heading(title, level=1)
            for run in heading.runs:
                run.font.color.rgb = theme_rgb
                run.font.size = Pt(template['section_size'])
            
            max_skills = 15 if template['compact'] else 20
            skills_para = document.add_paragraph('  •  '.join(skills[:max_skills]))
            for run in skills_para.runs:
                run.font.size = Pt(template['body_size'])
        
        # Save to buffer
        buffer = io.BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer.read()
    
    def analyze_ats_compatibility(self, resume_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resume for ATS compatibility"""
        issues = []
        suggestions = []
        score = 100
        
        personal = resume_content.get('personalInfo', resume_content.get('personal', {}))
        
        # Check essential sections
        if not personal.get('summary') and not resume_content.get('summary'):
            issues.append("Missing professional summary")
            score -= 10
        
        if not resume_content.get('skills'):
            issues.append("Missing skills section")
            score -= 15
        
        experiences = resume_content.get('experiences', resume_content.get('experience', []))
        if len(experiences) == 0:
            issues.append("No work experience listed")
            score -= 20
        
        if len(resume_content.get('education', [])) == 0:
            suggestions.append("Consider adding education details")
            score -= 5
        
        # Check content quality
        for exp in experiences:
            company = exp.get('company', 'your roles')
            if not exp.get('description') and not exp.get('highlights') and not exp.get('achievements'):
                suggestions.append(f"Add achievements for {company}")
        
        return {
            "score": max(0, min(100, score)),
            "issues": issues,
            "suggestions": suggestions,
            "format_issues": []
        }


# Singleton
resume_builder = ResumeBuilder()
