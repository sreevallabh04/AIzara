# -*- coding: utf-8 -*-
"""
Quick Gmail Test - Verify your app password
"""

import smtplib
import ssl

def test_gmail_login():
    """Test Gmail login with app password."""
    print("🧪 Testing Gmail Login")
    print("="*30)
    
    email = "srivallabhkakaral@gmail.com"
    
    # You'll enter the new app password here
    print("Please enter your Gmail app password (16 characters, no spaces):")
    print("Get it from: https://myaccount.google.com/apppasswords")
    app_password = input("App Password: ").strip()
    
    if not app_password:
        print("❌ No password entered")
        return False
    
    print(f"\n📧 Testing: {email}")
    print(f"🔑 Password: {'*' * len(app_password)}")
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(email, app_password)
            print("✅ SUCCESS! Gmail authentication working!")
            
            # Show the correct format
            print(f"\n📋 Your working credentials:")
            print(f"Email: {email}")
            print(f"App Password: {app_password}")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure 2FA is enabled on your Google account")
        print("2. Generate a NEW app password at https://myaccount.google.com/apppasswords")
        print("3. Use the 16-character password (no spaces)")
        print("4. Try again with the new password")
        
        return False

if __name__ == "__main__":
    success = test_gmail_login()
    if success:
        print("\n🎉 Ready to set up Zara with your Gmail!")
        print("Once verified, I'll update the Zara configuration.")
    else:
        print("\n🔄 Please get a new app password and try again.") 