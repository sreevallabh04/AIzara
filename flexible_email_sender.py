# -*- coding: utf-8 -*-
"""
Flexible Email Sender - Configure for any email provider
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_flexible(to, subject, body, 
                       sender_email="your_email@example.com",
                       sender_password="your_password",
                       smtp_server="smtp.gmail.com",
                       smtp_port=587):
    """
    Flexible email sender that works with any email provider.
    
    For Gmail:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        Use app password (not regular password)
    
    For Outlook/Hotmail:
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = 587
    
    For Yahoo:
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = 587
    
    Usage:
        result = send_email_flexible(
            to="recipient@example.com",
            subject="Test Email",
            body="Hello from Python!",
            sender_email="your_gmail@gmail.com",
            sender_password="your_app_password",
            smtp_server="smtp.gmail.com",
            smtp_port=587
        )
        print(result)
    """
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return f"✅ Email sent successfully to {to}"
        
    except Exception as e:
        return f"❌ Failed to send email: {e}"

# Example configurations:

def send_via_gmail(to, subject, body):
    """Send email via Gmail (recommended - most reliable)"""
    return send_email_flexible(
        to=to,
        subject=subject,
        body=body,
        sender_email="your_gmail@gmail.com",  # Replace with your Gmail
        sender_password="your_app_password",   # Replace with Gmail app password
        smtp_server="smtp.gmail.com",
        smtp_port=587
    )

def send_via_outlook(to, subject, body):
    """Send email via Outlook/Hotmail"""
    return send_email_flexible(
        to=to,
        subject=subject, 
        body=body,
        sender_email="your_email@outlook.com",  # Replace with your Outlook email
        sender_password="your_password",        # Replace with password
        smtp_server="smtp-mail.outlook.com",
        smtp_port=587
    )

def send_via_vit(to, subject, body):
    """Send email via VIT (configure as needed)"""
    return send_email_flexible(
        to=to,
        subject=subject,
        body=body,
        sender_email="sreevalllabh.2022@vitstudent.ac.in",
        sender_password="wheredobrokenheartsgo",
        smtp_server="mail.vit.ac.in",  # Try different VIT servers
        smtp_port=587
    )

# Test the functions:
if __name__ == "__main__":
    # Uncomment and modify to test:
    # result = send_via_gmail("test@example.com", "Test", "Hello!")
    # print(result)
    pass
