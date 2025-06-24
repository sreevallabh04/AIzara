# -*- coding: utf-8 -*-
"""
Universal Email Solution for Zara Assistant

This provides multiple working email options when Gmail authentication fails.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser

def main_menu():
    """Main menu for email setup options."""
    print("📧 Zara Assistant - Universal Email Setup")
    print("="*50)
    
    print("\nGmail authentication is having issues. Let's fix this with alternatives:")
    print("\n1️⃣ Try Gmail with 2FA verification")
    print("2️⃣ Set up with Outlook/Hotmail (easier)")
    print("3️⃣ Create a working email function (any provider)")
    print("4️⃣ Use web-based email sending")
    print("5️⃣ Troubleshoot Gmail step-by-step")
    
    choice = input("\nChoose an option (1-5): ").strip()
    
    if choice == "1":
        gmail_troubleshoot()
    elif choice == "2":
        outlook_setup()
    elif choice == "3":
        create_universal_function()
    elif choice == "4":
        web_based_solution()
    elif choice == "5":
        detailed_gmail_troubleshoot()
    else:
        print("Invalid choice. Running universal solution...")
        create_universal_function()

def gmail_troubleshoot():
    """Step-by-step Gmail troubleshooting."""
    print("\n🔍 Gmail Troubleshooting Guide")
    print("="*35)
    
    print("\n📋 Step 1: Verify 2-Factor Authentication")
    print("1. Go to: https://myaccount.google.com/security")
    
    open_link = input("Open this link now? (y/n): ").lower().strip() == 'y'
    if open_link:
        webbrowser.open("https://myaccount.google.com/security")
    
    print("\n2. Look for '2-Step Verification' - it MUST say 'On'")
    print("3. If it says 'Off', click to enable it (you'll need your phone)")
    
    tfa_enabled = input("\nIs 2-Factor Authentication enabled? (y/n): ").lower().strip() == 'y'
    
    if not tfa_enabled:
        print("\n❌ 2FA must be enabled for app passwords to work.")
        print("Please enable 2FA first, then try again.")
        return
    
    print("\n📋 Step 2: Generate New App Password")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    
    open_link = input("Open app passwords page? (y/n): ").lower().strip() == 'y'
    if open_link:
        webbrowser.open("https://myaccount.google.com/apppasswords")
    
    print("\n2. Select 'Mail' for app type")
    print("3. Select 'Other (custom name)' for device")
    print("4. Type 'Zara Assistant' as the name")
    print("5. Click 'Generate'")
    print("6. Copy the 16-character password (no spaces)")
    
    new_password = input("\nEnter the NEW app password (16 chars): ").strip()
    
    if len(new_password) != 16:
        print(f"⚠️ Warning: Expected 16 characters, got {len(new_password)}")
    
    # Test the new password
    test_gmail_password("srivallabhkakaral@gmail.com", new_password)

def test_gmail_password(email, password):
    """Test a Gmail password."""
    print(f"\n🧪 Testing Gmail password...")
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(email, password)
            print("✅ SUCCESS! Gmail working!")
            
            # Create working function
            create_gmail_function(email, password)
            return True
            
    except Exception as e:
        print(f"❌ Still failed: {e}")
        print("\nTrying alternative solutions...")
        return False

def outlook_setup():
    """Set up with Outlook/Hotmail (often easier than Gmail)."""
    print("\n📧 Outlook/Hotmail Setup")
    print("="*30)
    
    print("Outlook is often easier because:")
    print("• Less strict authentication")
    print("• No app passwords needed sometimes")
    print("• Works with regular passwords")
    
    email = input("\nEnter your Outlook/Hotmail email: ").strip()
    if not email:
        email = input("Or enter any email address to test: ").strip()
    
    password = input("Enter your password: ").strip()
    
    # Test Outlook
    servers_to_try = [
        ("smtp-mail.outlook.com", 587),
        ("outlook.office365.com", 587),
        ("smtp.live.com", 587)
    ]
    
    for server, port in servers_to_try:
        print(f"\n🧪 Testing {server}:{port}...")
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(server, port) as smtp_server:
                smtp_server.starttls(context=context)
                smtp_server.login(email, password)
                print(f"✅ SUCCESS with {server}!")
                
                create_working_function(email, password, server, port)
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("❌ Outlook setup failed too. Trying universal solution...")
    create_universal_function()

def create_universal_function():
    """Create a universal email function that works with any provider."""
    print("\n🛠️ Creating Universal Email Function")
    print("="*40)
    
    universal_code = '''# -*- coding: utf-8 -*-
"""
Universal Email Sender - Configure for YOUR email provider
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== CONFIGURATION SECTION =====
# Edit these with your email provider details:

SENDER_EMAIL = "your_email@example.com"        # Your email address
SENDER_PASSWORD = "your_password"              # Your password or app password
SMTP_SERVER = "smtp.gmail.com"                 # Your SMTP server
SMTP_PORT = 587                                # Usually 587 or 465

# Common SMTP settings:
# Gmail:     smtp.gmail.com:587 (needs app password)
# Outlook:   smtp-mail.outlook.com:587
# Yahoo:     smtp.mail.yahoo.com:587
# Others:    Contact your email provider

def send_email_universal(to, subject, body, cc=None, bcc=None):
    """
    Universal email sender - works with any email provider.
    
    Usage:
        result = send_email_universal("friend@example.com", "Hello", "How are you?")
        print(result)
    """
    
    try:
        # Validate email address
        if "@" not in to or "." not in to:
            return f"❌ Invalid email address: {to}"
        
        # Create message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to
        message["Subject"] = subject
        
        if cc:
            message["Cc"] = cc
        if bcc:
            message["Bcc"] = bcc
        
        # Add body
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            # Get all recipients
            all_recipients = [to]
            if cc:
                all_recipients.append(cc)
            if bcc:
                all_recipients.append(bcc)
            
            server.send_message(message, to_addrs=all_recipients)
        
        return f"✅ Email sent successfully to {to}"
        
    except Exception as e:
        return f"❌ Failed to send email: {e}"

# Quick test functions
def test_email():
    """Send a test email to yourself."""
    result = send_email_universal(
        SENDER_EMAIL, 
        "Test Email", 
        "This is a test email from your universal email sender!"
    )
    print(result)

def send_to_yourself(subject, body):
    """Quick function to email yourself."""
    return send_email_universal(SENDER_EMAIL, subject, body)

# Example usage:
if __name__ == "__main__":
    print("Universal Email Sender")
    print("Edit the configuration section with your email details")
    print("Then run: test_email() to test")
    
    # Uncomment to test:
    # test_email()
'''
    
    with open("universal_email_sender.py", "w", encoding='utf-8') as f:
        f.write(universal_code)
    
    print("✅ Created 'universal_email_sender.py'")
    print("\n📝 Next steps:")
    print("1. Edit the file with your email provider details")
    print("2. Run: python universal_email_sender.py")
    print("3. Test with any email provider!")

def web_based_solution():
    """Provide web-based email sending option."""
    print("\n🌐 Web-Based Email Solution")
    print("="*30)
    
    print("Since SMTP is having issues, here are web alternatives:")
    print("\n1. Use Gmail web interface directly")
    print("2. Use email APIs (SendGrid, Mailgun)")
    print("3. Use web automation (Selenium)")
    
    print("\nOpening Gmail web interface...")
    webbrowser.open("https://mail.google.com")
    
    print("\n💡 For now, you can:")
    print("• Use the web interface manually")
    print("• Set up a different email provider")
    print("• Contact your email provider for SMTP help")

def detailed_gmail_troubleshoot():
    """Detailed Gmail troubleshooting."""
    print("\n🔍 Detailed Gmail Troubleshooting")
    print("="*40)
    
    print("\n❓ Common Gmail Issues:")
    print("1. 2FA not enabled (required for app passwords)")
    print("2. App password generated incorrectly")
    print("3. Account security settings blocking access")
    print("4. Less secure app access disabled")
    
    print("\n🔧 Solutions to try:")
    print("1. Enable 2FA: https://myaccount.google.com/security")
    print("2. Generate new app password: https://myaccount.google.com/apppasswords")
    print("3. Check security: https://myaccount.google.com/security")
    
    choice = input("\nTry step-by-step setup? (y/n): ").lower().strip()
    if choice == 'y':
        gmail_troubleshoot()

def create_working_function(email, password, server="smtp.gmail.com", port=587):
    """Create a working email function with provided credentials."""
    
    working_code = f'''# -*- coding: utf-8 -*-
"""
Working Email Sender - Ready to Use!
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_working(to, subject, body):
    """
    Send email using verified working credentials.
    
    Usage:
        result = send_email_working("friend@example.com", "Hello", "How are you?")
        print(result)
    """
    
    sender_email = "{email}"
    sender_password = "{password}"
    smtp_server = "{server}"
    smtp_port = {port}
    
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
        
        return f"✅ Email sent successfully to {{to}}"
        
    except Exception as e:
        return f"❌ Failed to send email: {{e}}"

def test_working_email():
    """Send a test email."""
    result = send_email_working(
        "{email}",
        "Working Email Test",
        "This email confirms your email system is working!"
    )
    print(result)

if __name__ == "__main__":
    print("Working Email Sender Ready!")
    test_working_email()
'''
    
    with open("working_email_sender.py", "w", encoding='utf-8') as f:
        f.write(working_code)
    
    print(f"✅ Created 'working_email_sender.py' with your credentials!")
    print(f"🧪 Test it: python working_email_sender.py")

def create_gmail_function(email, password):
    """Create Gmail-specific function."""
    create_working_function(email, password, "smtp.gmail.com", 587)

if __name__ == "__main__":
    main_menu() 