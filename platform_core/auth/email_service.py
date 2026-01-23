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
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@ai-orchestrator.com")

    async def send_email(self, to_email: str, subject: str, body: str):
        """Send an email using SMTP or AI-validated Simulation"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_pass]):
            logger.warning(f"🚀 AI Power-Up: SMTP not configured. Simulating delivery to {to_email} via IA validation.")
            # Verify the email intent via AI
            if self.orchestrator:
                await self.orchestrator.universal_agent.act(f"Verify and audit this outgoing email: {subject}", {"to": to_email, "body": body})
            return True

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

    async def send_password_reset_email(self, email: str, token: str):
        """AI-generated password reset email"""
        if not self.orchestrator:
             # Basic template if AI is down
             return await self.send_email(email, "Reset Password", f"Token: {token}")

        task = f"Generate a professional password reset email for user {email}."
        context = {
            "type": "email_generation",
            "token": token,
            "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:4200"),
            "requirements": "The email should be secure, professional, and contain a clear call-to-action link."
        }
        
        result = await self.orchestrator.universal_agent.act(task, context)
        body = result.get("solution", "Reset Link: " + token)
        return await self.send_email(email, "Reset Your AI Orchestrator Password", body)

    async def send_ai_notification(self, email: str, alert_type: str, details: Dict[str, Any]):
        """Dynamically generate and send an alert via AI"""
        if not self.orchestrator: return False
        
        task = f"Generate a security/system alert email for {alert_type}."
        result = await self.orchestrator.universal_agent.act(task, {"details": details})
        
        return await self.send_email(email, f"AI Orchestrator Alert: {alert_type}", result.get("solution"))

# Instantiate with container access later if needed, but the main app handles it
email_service = EmailService()
