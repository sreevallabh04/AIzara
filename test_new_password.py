# -*- coding: utf-8 -*-
"""
Test New Gmail App Password
"""

import smtplib
import ssl

def test_new_gmail_password():
    """Test a new Gmail app password interactively."""
    print("🔐 Test New Gmail App Password")
    print("="*35)
    
    email = "srivallabhkakaral@gmail.com"
    
    print(f"📧 Email: {email}")
    print("\n📋 Steps to get a new app password:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Make sure '2-Step Verification' is ON")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print("4. Select 'Mail' -> 'Other (custom name)' -> 'Zara Assistant'")
    print("5. Copy the 16-character password")
    
    new_password = input("\n🔑 Enter your NEW app password: ").strip()
    
    if len(new_password) != 16:
        print(f"⚠️ Warning: App passwords are usually 16 characters. You entered {len(new_password)} characters.")
        confirm = input("Continue anyway? (y/n): ").lower().strip()
        if confirm != 'y':
            return False
    
    print(f"\n🧪 Testing: {email}")
    print(f"🔑 Password: {'*' * len(new_password)}")
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(email, new_password)
            print("✅ SUCCESS! Gmail authentication working!")
            
            # Send test email
            send_success_test(server, email, new_password)
            return new_password
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("\n🔧 Common issues:")
        print("• 2-Factor Authentication must be enabled")
        print("• Generate a brand new app password")
        print("• Make sure you copied the entire 16-character password")
        print("• Don't use your regular Gmail password")
        
        return False

def send_success_test(server, email, password):
    """Send a success confirmation email."""
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart()
        message["From"] = email
        message["To"] = email
        message["Subject"] = "🎉 Zara Assistant Gmail - WORKING!"
        
        body = """SUCCESS! 🎉

Your Gmail is now properly configured with Zara Assistant!

✅ Authentication: Working
✅ Email sending: Working
✅ Integration: Ready

You can now use Zara to send emails with commands like:
• "Send an email to someone@example.com"
• "Email my friend about the project"

This email confirms everything is set up correctly.

Best regards,
Zara Assistant
"""
        
        message.attach(MIMEText(body, "plain"))
        server.send_message(message)
        
        print(f"📧 Success email sent to {email}!")
        print(f"📬 Check your Gmail inbox!")
        
    except Exception as e:
        print(f"⚠️ Login worked but email failed: {e}")

if __name__ == "__main__":
    print("Gmail App Password Tester")
    result = test_new_gmail_password()
    
    if result:
        print(f"\n🎯 READY FOR ZARA INTEGRATION!")
        print(f"Working password: {result}")
        print(f"\nNext: I'll update Zara with your working credentials!")
    else:
        print(f"\n🔄 Please try again with a fresh app password from Google.") 