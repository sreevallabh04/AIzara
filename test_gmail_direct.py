# -*- coding: utf-8 -*-
"""
Direct Gmail Test with the provided app password
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_direct():
    """Test Gmail with the exact app password provided."""
    print("🧪 Testing Gmail with Your App Password")
    print("="*40)
    
    email = "srivallabhkakaral@gmail.com"
    
    # Test different formats of the app password
    app_passwords_to_test = [
        "xjcc fskn aoiu nvet",  # Original with spaces
        "xjccfsknaoiunvet",     # No spaces
        "xjcc-fskn-aoiu-nvet",  # With dashes
    ]
    
    for i, password in enumerate(app_passwords_to_test, 1):
        print(f"\n🔍 Test {i}: '{password}'")
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=context)
                server.login(email, password)
                print(f"✅ SUCCESS! Working password format: '{password}'")
                
                # Send a test email to confirm it fully works
                send_test_email(server, email, password)
                return password
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print(f"\n❌ None of the password formats worked.")
    print(f"💡 The app password might need to be regenerated.")
    return None

def send_test_email(server, email, password):
    """Send a quick test email to verify full functionality."""
    try:
        # Create test message
        message = MIMEMultipart()
        message["From"] = email
        message["To"] = email  # Send to self
        message["Subject"] = "✅ Zara Assistant Gmail Test - Success!"
        
        body = """🎉 CONGRATULATIONS! 

Your Gmail integration with Zara Assistant is working perfectly!

✅ SMTP Authentication: Success
✅ Email Composition: Success  
✅ Email Sending: Success

You can now use Zara to send emails with commands like:
- "Send an email to someone@example.com"
- "Email my friend about the meeting"

This test email confirms everything is set up correctly.

Best regards,
Zara Assistant 🤖
"""
        
        message.attach(MIMEText(body, "plain"))
        server.send_message(message)
        
        print(f"📧 Test email sent to {email}!")
        print(f"📬 Check your inbox for confirmation!")
        
    except Exception as e:
        print(f"⚠️ Login worked but email sending failed: {e}")

if __name__ == "__main__":
    working_password = test_gmail_direct()
    
    if working_password:
        print(f"\n🎉 GMAIL SETUP SUCCESSFUL!")
        print(f"Working password: '{working_password}'")
        print(f"\n📋 Ready to integrate with Zara!")
        
        # Create the working email function
        create_working_function(working_password)
    else:
        print(f"\n🔄 TROUBLESHOOTING NEEDED")
        print(f"Please try:")
        print(f"1. Go to https://myaccount.google.com/apppasswords")
        print(f"2. Generate a NEW app password")
        print(f"3. Make sure 2FA is enabled")
        print(f"4. Try the new password")

def create_working_function(password):
    """Create the final working email function."""
    
    working_code = f'''# -*- coding: utf-8 -*-
"""
Working Gmail Sender for Zara Assistant
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_now(to, subject, body):
    """
    Send email immediately using verified Gmail credentials.
    
    Usage:
        result = send_email_now("friend@example.com", "Hello", "How are you?")
        print(result)
    """
    
    sender_email = "srivallabhkakaral@gmail.com"
    sender_password = "{password}"
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return f"✅ Email sent successfully to {{to}}"
        
    except Exception as e:
        return f"❌ Failed to send email: {{e}}"

# Quick test function
def test_send():
    """Send a test email to yourself."""
    result = send_email_now(
        "srivallabhkakaral@gmail.com", 
        "Test from Zara", 
        "This is a test email from your working email setup!"
    )
    print(result)

if __name__ == "__main__":
    print("Gmail email sender ready!")
    print("Try: test_send() to send yourself a test email")
'''
    
    with open("working_gmail_sender.py", "w", encoding='utf-8') as f:
        f.write(working_code)
    
    print(f"💾 Created 'working_gmail_sender.py'")
    print(f"🧪 Test it with: python working_gmail_sender.py") 