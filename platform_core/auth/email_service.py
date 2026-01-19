"""
Email Service - Handles core communications (Password Reset, Alerts)
"""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@ai-orchestrator.com")
        self.use_mock = os.getenv("EMAIL_MOCK", "true").lower() == "true"

    def send_email(self, to_email: str, subject: str, body: str):
        """Send an email using SMTP or mock to logger"""
        if self.use_mock:
            logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body[:100]}...")
            print(f"\n--- MOCK EMAIL SENT ---\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n-----------------------\n")
            return True

        if not all([self.smtp_host, self.smtp_user, self.smtp_pass]):
            logger.error("SMTP configuration missing. Email not sent.")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_password_reset_email(self, email: str, token: str):
        """Send password reset link"""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
        reset_link = f"{frontend_url}/auth/reset-password?token={token}"
        
        subject = "Reset Your AI Orchestrator Password"
        body = f"""
        <h2>Password Reset Request</h2>
        <p>You requested a password reset for your AI Orchestrator account.</p>
        <p>Click the link below to set a new password. This link expires in 1 hour.</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>If you did not request this, please ignore this email.</p>
        """
        return self.send_email(email, subject, body)

email_service = EmailService()
