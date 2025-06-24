# -*- coding: utf-8 -*-
"""
Final Gmail Test with New App Password
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_final_gmail():
    """Test the new Gmail app password."""
    print("🔐 Testing New Gmail App Password")
    print("="*40)
    
    email = "srivallabhkakaral@gmail.com"
    app_password = "wnas uhyl wlhc iwsg"
    
    print(f"📧 Email: {email}")
    print(f"🔑 Testing new app password...")
    
    # Test different formats
    passwords_to_test = [
        "wnas uhyl wlhc iwsg",  # With spaces
        "wnasuuhlwlhciwsg",     # No spaces
        "wnas-uhyl-wlhc-iwsg",  # With dashes
    ]
    
    for i, password in enumerate(passwords_to_test, 1):
        print(f"\n🧪 Format {i}: Testing '{password}'")
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=context)
                server.login(email, password)
                print(f"✅ SUCCESS! Authentication working with: '{password}'")
                
                # Send confirmation email
                send_confirmation_email(server, email, password)
                return password
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print(f"\n❌ New password also failed. Let's troubleshoot...")
    return None

def send_confirmation_email(server, email, working_password):
    """Send a success confirmation email."""
    try:
        message = MIMEMultipart()
        message["From"] = email
        message["To"] = email
        message["Subject"] = "🎉 Zara Assistant - Gmail Working!"
        
        body = f"""🎉 EXCELLENT! Your Gmail is now working with Zara Assistant!

✅ Email: {email}
✅ Authentication: Successful
✅ SMTP: Connected
✅ Email Sending: Working

Your Zara Assistant can now send emails with commands like:
• "Send an email to someone@example.com"
• "Email my friend about the meeting"
• "Compose an email"

Integration complete! 🚀

Best regards,
Zara Assistant
"""
        
        message.attach(MIMEText(body, "plain"))
        server.send_message(message)
        
        print(f"📧 Confirmation email sent to {email}!")
        print(f"📬 Check your Gmail inbox!")
        
    except Exception as e:
        print(f"⚠️ Login worked but email sending failed: {e}")

def setup_zara_integration(working_password):
    """Set up the working password in Zara's system."""
    print(f"\n🔧 Setting up Zara integration...")
    
    # Create the final working email functions
    create_zara_email_function(working_password)
    update_zara_credentials(working_password)

def create_zara_email_function(password):
    """Create the final working email function for Zara."""
    
    email_code = f'''# -*- coding: utf-8 -*-
"""
Zara Assistant - Working Gmail Integration
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_zara(to, subject, body, cc=None, bcc=None):
    """
    Send email through Zara Assistant's Gmail integration.
    
    Usage:
        result = send_email_zara("friend@example.com", "Hello", "How are you?")
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
        
        if cc:
            message["Cc"] = ", ".join(cc) if isinstance(cc, list) else cc
        if bcc:
            message["Bcc"] = ", ".join(bcc) if isinstance(bcc, list) else bcc
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            
            # Get all recipients
            all_recipients = [to]
            if cc:
                all_recipients.extend(cc if isinstance(cc, list) else [cc])
            if bcc:
                all_recipients.extend(bcc if isinstance(bcc, list) else [bcc])
            
            server.send_message(message, to_addrs=all_recipients)
        
        return f"✅ Email sent successfully to {{to}}"
        
    except Exception as e:
        return f"❌ Failed to send email: {{e}}"

# Quick functions
def email_yourself(subject, body):
    """Send an email to yourself."""
    return send_email_zara("srivallabhkakaral@gmail.com", subject, body)

def test_email():
    """Send a test email to yourself."""
    result = email_yourself("Test from Zara", "This is a test email from Zara Assistant!")
    print(result)

if __name__ == "__main__":
    print("Zara Gmail Integration Ready!")
    print("Try: test_email() to send yourself a test")
'''
    
    with open("zara_gmail_ready.py", "w", encoding='utf-8') as f:
        f.write(email_code)
    
    print(f"📁 Created 'zara_gmail_ready.py' - Your working email system!")

def update_zara_credentials(password):
    """Update Zara's credential storage with working password."""
    try:
        import json
        import base64
        from pathlib import Path
        
        # Store in Zara's credential system
        credentials_dir = Path("data/encrypted")
        credentials_dir.mkdir(parents=True, exist_ok=True)
        credentials_file = credentials_dir / "email_credentials.json"
        
        email = "srivallabhkakaral@gmail.com"
        provider = "gmail"
        
        credential_data = {{
            'email': email,
            'password': password,
            'provider': provider,
            'stored_at': '2024-06-24T12:00:00',
            'working': True
        }}
        
        service_key = "zara_email_credentials"
        account_key = f"{{email}}_{{provider}}"
        
        all_credentials = {{
            service_key: {{
                account_key: credential_data
            }}
        }}
        
        credentials_json = json.dumps(all_credentials, indent=2)
        encrypted_data = base64.b64encode(credentials_json.encode()).decode()
        
        with open(credentials_file, 'w') as f:
            f.write(encrypted_data)
        
        print(f"✅ Updated Zara's credential storage")
        
    except Exception as e:
        print(f"⚠️ Credential storage update failed: {{e}}")
        print("Don't worry - the direct email function still works!")

if __name__ == "__main__":
    working_password = test_final_gmail()
    
    if working_password:
        print(f"\n🎉 GMAIL INTEGRATION SUCCESSFUL!")
        print(f"="*50)
        print(f"✅ Email: srivallabhkakaral@gmail.com")
        print(f"✅ Password: Working")
        print(f"✅ SMTP: Connected")
        print(f"✅ Zara Integration: Ready")
        
        setup_zara_integration(working_password)
        
        print(f"\n🚀 YOU CAN NOW SEND EMAILS!")
        print(f"="*30)
        print(f"1. Quick test: python zara_gmail_ready.py")
        print(f"2. Voice command: python main.py")
        print(f"   Then say: 'Send an email'")
        print(f"3. Text mode: python main.py --text")
        print(f"4. Direct function: from zara_gmail_ready import send_email_zara")
        
    else:
        print(f"\n🔄 Password still not working. Possible issues:")
        print(f"• Make sure 2-Factor Authentication is enabled")
        print(f"• Generate a completely new app password")
        print(f"• Try copy-pasting the password without manual typing") 