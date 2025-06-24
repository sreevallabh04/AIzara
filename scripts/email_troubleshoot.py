# -*- coding: utf-8 -*-
"""
Email Troubleshooting and Setup Guide
"""

import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def troubleshoot_vit_email():
    """Troubleshoot VIT email authentication issues."""
    print("🔧 VIT Email Troubleshooting Guide")
    print("="*50)
    
    email = "sreevalllabh.2022@vitstudent.ac.in"
    print(f"📧 Email: {email}")
    
    print("\n❌ Authentication Failed (Error 535)")
    print("This typically means one of the following:")
    print("\n1. 🔐 Password is incorrect")
    print("2. 🔒 Two-factor authentication is enabled")
    print("3. 📱 App-specific password required")
    print("4. 🏢 VIT uses different SMTP settings")
    print("5. 🌐 Account needs to be enabled for SMTP")
    
    print("\n🔍 TROUBLESHOOTING STEPS:")
    print("="*30)
    
    print("\n1️⃣ Verify Password:")
    print("   - Try logging into VIT webmail with the same password")
    print("   - Check for any recent password changes")
    
    print("\n2️⃣ Check VIT Email Settings:")
    print("   - VIT might use different SMTP servers")
    print("   - Common alternatives:")
    print("     • mail.vit.ac.in")
    print("     • smtp.vit.ac.in") 
    print("     • outlook.office365.com")
    
    print("\n3️⃣ Enable App Passwords:")
    print("   - Log into VIT email portal")
    print("   - Look for 'App Passwords' or 'Security' settings")
    print("   - Generate a new app password for email clients")
    
    print("\n4️⃣ Check Two-Factor Authentication:")
    print("   - If 2FA is enabled, you need an app password")
    print("   - Disable 2FA temporarily to test")
    
    # Test different SMTP servers
    test_smtp_servers(email)
    
    # Provide working alternatives
    provide_alternatives()

def test_smtp_servers(email):
    """Test different SMTP server configurations."""
    print(f"\n🧪 Testing Different SMTP Servers:")
    print("="*40)
    
    servers_to_test = [
        ("smtp-mail.outlook.com", 587),
        ("outlook.office365.com", 587),
        ("mail.vit.ac.in", 587),
        ("smtp.vit.ac.in", 587),
        ("smtp.vit.ac.in", 25),
        ("mail.vit.ac.in", 25),
    ]
    
    for server, port in servers_to_test:
        print(f"\n🔌 Testing {server}:{port}...")
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(server, port, timeout=10) as smtp_server:
                smtp_server.starttls(context=context)
                print(f"   ✅ Connection successful to {server}:{port}")
                print(f"   📋 Server capabilities: {smtp_server.esmtp_features}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

def provide_alternatives():
    """Provide alternative email sending methods."""
    print(f"\n🔄 ALTERNATIVE SOLUTIONS:")
    print("="*30)
    
    print("\n1️⃣ Use Personal Gmail:")
    print("   - Set up a Gmail account")
    print("   - Generate app password")
    print("   - Use Gmail SMTP (works reliably)")
    
    print("\n2️⃣ VIT IT Support:")
    print("   - Contact VIT IT helpdesk")
    print("   - Ask for SMTP configuration details")
    print("   - Request app password setup")
    
    print("\n3️⃣ Use Email API Services:")
    print("   - SendGrid")
    print("   - Mailgun") 
    print("   - Amazon SES")
    
    print("\n4️⃣ Working Email Function (Using Any Provider):")
    print("   Here's a template you can modify:")
    
    create_flexible_email_template()

def create_flexible_email_template():
    """Create a flexible email template that works with any provider."""
    
    template_code = '''# -*- coding: utf-8 -*-
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
'''
    
    # Save the template
    with open("flexible_email_sender.py", "w", encoding='utf-8') as f:
        f.write(template_code)
    
    print(f"\n💾 Created 'flexible_email_sender.py'")
    print("   ✏️  Edit this file with your email credentials")
    print("   🧪 Test with different providers")

def show_next_steps():
    """Show recommended next steps."""
    print(f"\n🎯 RECOMMENDED NEXT STEPS:")
    print("="*30)
    
    print("\n1. 📞 Contact VIT IT Support:")
    print("   - Ask for correct SMTP settings")
    print("   - Request app password setup")
    print("   - Email: it@vit.ac.in (or check VIT portal)")
    
    print("\n2. 🔄 Try Alternative Email:")
    print("   - Set up Gmail with app password")
    print("   - Use the flexible_email_sender.py script")
    print("   - Test with known working email")
    
    print("\n3. 🔍 Debug Further:")
    print("   - Check VIT email portal settings")
    print("   - Look for SMTP/IMAP configuration")
    print("   - Try different ports (25, 465, 587)")
    
    print("\n4. ✅ Once Working:")
    print("   - Update Zara's email plugin")
    print("   - Test with: python main.py")
    print("   - Say: 'send an email'")

if __name__ == "__main__":
    troubleshoot_vit_email()
    show_next_steps()
    
    print(f"\n📋 SUMMARY:")
    print("- VIT email authentication failed (common issue)")
    print("- Multiple solutions provided")
    print("- Flexible email template created")
    print("- Contact VIT IT for proper SMTP settings") 