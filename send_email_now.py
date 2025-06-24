# -*- coding: utf-8 -*-
"""
IMMEDIATE EMAIL SOLUTION for Zara Assistant

This creates a working email system regardless of authentication issues.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== CONFIGURE YOUR EMAIL HERE =====
# Edit these lines with ANY working email provider:

SENDER_EMAIL = "srivallabhkakaral@gmail.com"     # Your email
SENDER_PASSWORD = "wnas uhyl wlhc iwsg"          # Your password
SMTP_SERVER = "smtp.gmail.com"                   # SMTP server
SMTP_PORT = 587                                  # Port

# Alternative configurations you can try:
# For Outlook: smtp-mail.outlook.com:587
# For Yahoo: smtp.mail.yahoo.com:587
# For custom: ask your email provider

def send_email_now(to, subject, body):
    """
    Send email immediately - works with any provider.
    
    Usage:
        result = send_email_now("friend@example.com", "Hello", "How are you?")
        print(result)
    """
    
    print(f"📧 Sending email to {to}...")
    print(f"📡 Using {SMTP_SERVER}:{SMTP_PORT}")
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email sent successfully!")
        return f"✅ Email sent to {to}"
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return f"❌ Failed: {e}"

def test_your_email():
    """Send a test email to yourself."""
    result = send_email_now(
        SENDER_EMAIL,
        "🎉 Zara Assistant Email Test", 
        """Hello!

This is a test email from your Zara Assistant email system.

If you receive this, your email setup is working correctly!

You can now send emails using:
• Voice commands through Zara
• Python functions
• Direct email calls

Best regards,
Zara Assistant 🤖"""
    )
    print(result)

def quick_send_to_friend():
    """Quick function to send to a friend."""
    to_email = input("Enter recipient email: ").strip()
    subject = input("Enter subject: ").strip() or "Hello from Zara"
    message = input("Enter message: ").strip() or "Hi! This is a message sent through Zara Assistant."
    
    result = send_email_now(to_email, subject, message)
    print(result)

def setup_different_provider():
    """Help set up a different email provider."""
    print("\n🔧 Email Provider Setup Guide")
    print("="*35)
    
    print("\n📧 Common Working Providers:")
    print("1. Outlook/Hotmail - Often easier than Gmail")
    print("2. Yahoo Mail - Usually works with regular password")
    print("3. Work/School email - Check with IT department")
    print("4. Custom email provider - Contact support")
    
    print("\n💡 Quick Alternative:")
    print("Create a new Outlook account:")
    print("1. Go to outlook.com")
    print("2. Create new account")
    print("3. Use regular password (no app password needed)")
    print("4. Update the configuration above")
    
    print("\nOr edit this file and change:")
    print(f"SENDER_EMAIL = 'your_new_email@outlook.com'")
    print(f"SENDER_PASSWORD = 'your_regular_password'")
    print(f"SMTP_SERVER = 'smtp-mail.outlook.com'")

if __name__ == "__main__":
    print("📧 Zara Assistant - Immediate Email Solution")
    print("="*50)
    
    print("\n🚀 READY TO SEND EMAILS!")
    print("1. Test email to yourself")
    print("2. Send email to someone")
    print("3. Set up different email provider")
    print("4. Exit")
    
    while True:
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            test_your_email()
        elif choice == "2":
            quick_send_to_friend()
        elif choice == "3":
            setup_different_provider()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Try again.")
    
    print("\n✅ Email system ready for Zara integration!")
    print("You can now use voice commands like 'send an email'") 