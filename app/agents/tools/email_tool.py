# Directory: yt-agentic-rag/app/agents/tools/email_tool.py

"""
Email Tool - Send Emails via Gmail API.

This tool allows the agent to send emails with:
- Plain text body
- Custom subject lines
- Sent from the configured corporate email

Uses Gmail API with service account authentication and
domain-wide delegation to send emails on behalf of users.
"""

import logging
import uuid
import asyncio
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .base import BaseTool
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class EmailTool(BaseTool):
    """
    Tool for sending real emails via SMTP using Gmail App Passwords.
    """
    
    def __init__(self):
        """Initialize the Email tool."""
        pass
    
    @property
    def name(self) -> str:
        """Tool name matching TOOL_DEFINITIONS."""
        return "send_email"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Send an email via SMTP"
    
    async def execute(
        self,
        to: str,
        subject: str,
        body: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a real email using SMTP.
        """
        # Validate required parameters
        is_valid, missing = self.validate_params(
            required=['to', 'subject', 'body'],
            provided={'to': to, 'subject': subject, 'body': body}
        )
        
        if not is_valid:
            return self._error_response(
                f"Missing required parameters: {', '.join(missing)}"
            )
            
        settings = get_settings()
        
        email_user = settings.email_user
        email_password = settings.email_app_password
        
        if not email_user or not email_password:
            logger.error("Email credentials are not configured in settings.")
            return self._error_response(
                "Email credentials are not configured on the server."
            )
        
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = to
            msg['Subject'] = subject

            # Attach the body text
            msg.attach(MIMEText(body, 'plain'))

            def _send():
                # Context manager guarantees the connection is closed on error
                with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
                    server.starttls()
                    server.login(email_user, email_password)
                    server.send_message(msg)

            # smtplib is blocking — run it off the event loop
            await asyncio.to_thread(_send)
            
            message_id = f"msg-{uuid.uuid4().hex[:10]}"
            
            logger.info(
                f"Email sent successfully: "
                f"ID={message_id}, To='{to}', Subject='{subject}'"
            )
            
            return self._success_response({
                "message_id": message_id,
                "to": to,
                "subject": subject,
                "from": email_user,
                "status": "delivered"
            })
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Failed to authenticate with SMTP server. Check app password.")
            return self._error_response(
                "SMTP Authentication failed. The app password may be invalid."
            )
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return self._error_response(
                f"Failed to send email: {str(e)}"
            )

# Global tool instance
email_tool = EmailTool()

