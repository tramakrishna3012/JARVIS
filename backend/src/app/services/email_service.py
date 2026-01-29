"""
Email Service - SMTP/IMAP Integration
"""

import asyncio
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import aiosmtplib
from app.core.config import settings


class EmailService:
    """Service for sending and receiving emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
    
    async def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        cc_addresses: Optional[List[str]] = None,
        attachments: Optional[List[tuple]] = None  # [(filename, content, mimetype)]
    ) -> bool:
        """Send an email via SMTP"""
        try:
            # Create message
            if attachments:
                message = MIMEMultipart()
                if is_html:
                    message.attach(MIMEText(body, 'html'))
                else:
                    message.attach(MIMEText(body, 'plain'))
                
                for filename, content, mimetype in attachments:
                    part = MIMEApplication(content, Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)
            else:
                message = MIMEText(body, 'html' if is_html else 'plain')
            
            message['From'] = self.smtp_user
            message['To'] = ', '.join(to_addresses)
            message['Subject'] = subject
            
            if cc_addresses:
                message['Cc'] = ', '.join(cc_addresses)
            
            # Send
            all_recipients = to_addresses + (cc_addresses or [])
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
            )
            
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    async def send_job_application_email(
        self,
        to_address: str,
        job_title: str,
        company: str,
        candidate_name: str,
        cover_letter: str,
        resume_pdf: bytes
    ) -> bool:
        """Send a job application email with resume attachment"""
        subject = f"Application for {job_title} - {candidate_name}"
        
        body = f"""
        <html>
        <body>
        <p>Dear Hiring Manager,</p>
        
        <p>{cover_letter.replace(chr(10), '<br>')}</p>
        
        <p>I have attached my resume for your review.</p>
        
        <p>Best regards,<br>
        {candidate_name}</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_addresses=[to_address],
            subject=subject,
            body=body,
            is_html=True,
            attachments=[
                (f"{candidate_name.replace(' ', '_')}_Resume.pdf", resume_pdf, "application/pdf")
            ]
        )
    
    async def send_referral_request_email(
        self,
        to_address: str,
        connection_name: str,
        message: str,
        candidate_name: str
    ) -> bool:
        """Send a referral request email"""
        subject = f"Referral Request from {candidate_name}"
        
        body = f"""
        <html>
        <body>
        <p>Hi {connection_name},</p>
        
        <p>{message.replace(chr(10), '<br>')}</p>
        
        <p>Thank you for considering my request.</p>
        
        <p>Best regards,<br>
        {candidate_name}</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_addresses=[to_address],
            subject=subject,
            body=body,
            is_html=True
        )


# Singleton
email_service = EmailService()
