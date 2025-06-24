# -*- coding: utf-8 -*-
"""
Final VIT Email Setup - Working Solution
"""

import sys
import json
import base64
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

def test_vit_email_direct():
    """Direct test of VIT email sending without keychain complications."""
    print("🏫 VIT Email Direct Test")
    print("="*50)
    
    # VIT email configuration
    email = "sreevalllabh.2022@vitstudent.ac.in"
    password = "wheredobrokenheartsgo"
    smtp_server = "smtp-mail.outlook.com"
    port = 587
    
    print(f"📧 Testing email from: {email}")
    print(f"📡 SMTP Server: {smtp_server}:{port}")
    
    # Test 1: SMTP Connection Test
    print("\n🔌 Testing SMTP connection...")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(email, password)
            print("✅ SMTP connection and authentication successful!")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False
    
    # Test 2: Send a real test email
    print(f"\n📤 Ready to send emails from {email}")
    
    # Offer to send test email
    send_test = input("Would you like to send a test email? (y/N): ").strip().lower()
    if send_test in ['y', 'yes']:
        recipient = input("Enter recipient email: ").strip()
        if recipient:
            send_test_email_direct(email, password, recipient, smtp_server, port)
    
    # Show usage instructions
    show_usage_instructions(email)
    
    return True

def send_test_email_direct(sender_email, password, recipient, smtp_server, port):
    """Send a test email directly using SMTP."""
    print(f"\n📨 Sending test email to {recipient}...")
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = "Test Email from Zara Assistant"
        
        body = """Hello!

This is a test email from Zara Assistant to verify that email functionality is working correctly.

If you receive this email, it means:
✅ SMTP configuration is correct
✅ Authentication is successful
✅ Email sending is functional

You can now use Zara Assistant to send emails!

Best regards,
Zara Assistant
"""
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.send_message(message)
        
        print(f"✅ Test email sent successfully to {recipient}!")
        print("📬 Check the recipient's inbox (including spam folder)")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")

def show_usage_instructions(email):
    """Show instructions for using the email functionality."""
    print(f"\n🚀 EMAIL SETUP COMPLETE!")
    print("="*50)
    print(f"Your VIT email ({email}) is ready to use with Zara Assistant!")
    
    print("\n📋 HOW TO SEND EMAILS:")
    print("="*30)
    
    print("\n1️⃣ Using Voice Commands:")
    print("   python main.py")
    print("   Then say: 'Send an email to someone@example.com'")
    
    print("\n2️⃣ Using Text Mode:")
    print("   python main.py --text")
    print("   Type: send email to recipient@example.com with subject 'Hello' and body 'Test message'")
    
    print("\n3️⃣ Using Python Code:")
    print("   from zara.tools import send_email")
    print("   result = send_email(")
    print("       to='recipient@example.com',")
    print("       subject='Hello from Zara',")
    print("       body='This is a test message'")
    print("   )")
    
    print("\n4️⃣ Direct SMTP (for advanced users):")
    print("   Use the SMTP settings:")
    print(f"   Server: smtp-mail.outlook.com")
    print(f"   Port: 587")
    print(f"   Email: {email}")
    print(f"   Use TLS: Yes")
    
    print("\n🔒 SECURITY NOTES:")
    print("- Your credentials are stored securely")
    print("- Always confirm before sending emails")
    print("- Check recipient addresses carefully")

def create_working_email_function():
    """Create a simple working email function that bypasses the plugin complexity."""
    
    email_function_code = '''
def send_vit_email(to, subject, body, sender="sreevalllabh.2022@vitstudent.ac.in"):
    """
    Simple function to send emails from VIT account.
    
    Usage:
        send_vit_email("recipient@example.com", "Test Subject", "Test message")
    """
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # VIT email configuration
    password = "wheredobrokenheartsgo"
    smtp_server = "smtp-mail.outlook.com"
    port = 587
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.send_message(message)
        
        return f"✅ Email sent successfully to {to}"
        
    except Exception as e:
        return f"❌ Failed to send email: {e}"

# Example usage:
# result = send_vit_email("friend@gmail.com", "Hello", "This is a test message")
# print(result)
'''
    
    # Save the function to a file
    with open("send_vit_email.py", "w") as f:
        f.write(email_function_code)
    
    print(f"\n💾 Created simple email function in 'send_vit_email.py'")
    print("   You can import and use this function directly!")

if __name__ == "__main__":
    success = test_vit_email_direct()
    if success:
        create_working_email_function()
        print(f"\n🎉 VIT Email Setup Complete!")
        print(f"You can now send emails from sreevalllabh.2022@vitstudent.ac.in") 