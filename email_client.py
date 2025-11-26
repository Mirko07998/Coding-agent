"""Email notification client for sending PR notifications."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class EmailClient:
    """Client for sending email notifications."""
    
    def __init__(self):
        """
        Initialize email client with SMTP configuration from environment.
        
        Required environment variables:
        - EMAIL_SMTP_SERVER: SMTP server address (e.g., smtp.gmail.com)
        - EMAIL_SMTP_PORT: SMTP port (e.g., 587 for TLS, 465 for SSL)
        - EMAIL_SENDER: Sender email address
        - EMAIL_SENDER_PASSWORD: Sender email password or app password
        - EMAIL_RECIPIENTS: Comma-separated list of recipient emails
        
        Optional:
        - EMAIL_USE_TLS: Use TLS (default: true for port 587)
        - EMAIL_USE_SSL: Use SSL (default: true for port 465)
        """
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.sender = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
        self.recipients = self._parse_recipients(os.getenv("EMAIL_RECIPIENTS", ""))
        self.use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
        self.use_ssl = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
        
        # Auto-detect TLS/SSL based on port if not explicitly set
        if self.smtp_port == 587 and os.getenv("EMAIL_USE_TLS") is None:
            self.use_tls = True
        elif self.smtp_port == 465 and os.getenv("EMAIL_USE_SSL") is None:
            self.use_ssl = True
    
    def _parse_recipients(self, recipients_str: str) -> List[str]:
        """Parse comma-separated recipient emails."""
        if not recipients_str:
            return []
        return [email.strip() for email in recipients_str.split(",") if email.strip()]
    
    def is_configured(self) -> bool:
        """
        Check if email client is properly configured.
        
        Returns:
            True if all required configuration is present
        """
        return all([
            self.smtp_server,
            self.smtp_port,
            self.sender,
            self.sender_password,
            self.recipients
        ])
    
    def send_notification(self, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """
        Send email notification.
        
        Args:
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            True if email was sent successfully
        """
        if not self.is_configured():
            print("⚠ Email not configured. Skipping email notification.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server and send
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.sender, self.sender_password)
            server.sendmail(self.sender, self.recipients, msg.as_string())
            server.quit()
            
            print(f"✓ Email notification sent to {', '.join(self.recipients)}")
            return True
            
        except Exception as e:
            print(f"⚠ Failed to send email notification: {str(e)}")
            return False
    
    def send_pr_notification(self, ticket_key: str, ticket_summary: str, 
                            pr_url: str, branch_name: str, 
                            files_generated: List[str], jira_url: Optional[str] = None) -> bool:
        """
        Send PR notification email with formatted content.
        
        Args:
            ticket_key: Jira ticket key
            ticket_summary: Ticket summary
            pr_url: Pull request URL
            branch_name: Branch name
            files_generated: List of generated file paths
            jira_url: Optional Jira ticket URL
            
        Returns:
            True if email was sent successfully
        """
        subject = f"✅ PR Created: {ticket_key} - {ticket_summary}"
        
        # Plain text body
        body = f"""
Automated Code Generation Complete

Ticket: {ticket_key}
Summary: {ticket_summary}

Pull Request: {pr_url}
Branch: {branch_name}

Files Generated ({len(files_generated)}):
{chr(10).join(f'  - {f}' for f in files_generated)}

"""
        if jira_url:
            body += f"Jira Ticket: {jira_url}\n"
        
        body += "\nGenerated by the autonomous coding agent."
        
        # HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
        .link {{ color: #0066cc; text-decoration: none; }}
        .link:hover {{ text-decoration: underline; }}
        .files {{ background-color: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>✅ Automated Code Generation Complete</h2>
    </div>
    <div class="content">
        <div class="info-box">
            <strong>Ticket:</strong> {ticket_key}<br>
            <strong>Summary:</strong> {ticket_summary}
        </div>
        
        <div class="info-box">
            <strong>Pull Request:</strong> <a href="{pr_url}" class="link">{pr_url}</a><br>
            <strong>Branch:</strong> {branch_name}
        </div>
        
        <div class="info-box">
            <strong>Files Generated ({len(files_generated)}):</strong>
            <div class="files">
{chr(10).join(f'  • {f}' for f in files_generated)}
            </div>
        </div>
"""
        if jira_url:
            html_body += f"""
        <div class="info-box">
            <strong>Jira Ticket:</strong> <a href="{jira_url}" class="link">{jira_url}</a>
        </div>
"""
        
        html_body += """
    </div>
    <div class="footer">
        <p>Generated by the autonomous coding agent</p>
    </div>
</body>
</html>
"""
        
        return self.send_notification(subject, body, html_body)

