# -*- coding: utf-8 -*-
"""
VIT Email Test Script - Complete email sending test
"""

import sys
import json
import base64
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_and_test_vit_email():
    """Setup and test VIT email functionality."""
    print("🏫 VIT Email Setup and Test")
    print("="*50)
    
    # Your VIT credentials
    email = "sreevalllabh.2022@vitstudent.ac.in"
    password = "wheredobrokenheartsgo"
    provider = "vit"
    
    try:
        from plugins.email_sender.plugin import create_plugin, EmailSender
        from zara.security.keychain import KeychainManager
        
        # Initialize with file storage
        keychain = KeychainManager(use_os_keychain=False)
        
        # Setup credentials directly
        print("📝 Setting up credentials...")
        
        # Create credential data manually
        credentials_dir = Path("data/encrypted")
        credentials_dir.mkdir(parents=True, exist_ok=True)
        credentials_file = credentials_dir / "email_credentials.json"
        
        credential_data = {
            'email': email,
            'password': password,
            'provider': provider,
            'stored_at': '2024-06-24T10:30:00'
        }
        
        # Store credentials with correct key format
        service_key = "zara_email_credentials"
        account_key = f"{email}_{provider}"
        
        all_credentials = {
            service_key: {
                account_key: credential_data
            }
        }
        
        # Simple base64 encoding
        credentials_json = json.dumps(all_credentials, indent=2)
        encrypted_data = base64.b64encode(credentials_json.encode()).decode()
        
        with open(credentials_file, 'w') as f:
            f.write(encrypted_data)
        
        print(f"✅ Credentials stored in {credentials_file}")
        
        # Test credential retrieval
        print("\n🔍 Testing credential retrieval...")
        email_sender = EmailSender(keychain_manager=keychain)
        retrieved_creds = email_sender.credentials.get_credentials(email, provider)
        
        if retrieved_creds:
            print(f"✅ Successfully retrieved credentials for {email}")
        else:
            print("❌ Failed to retrieve credentials")
            return
        
        # Test email composition (dry run)
        print("\n📧 Testing email composition...")
        
        test_result = email_sender.send_email(
            sender_email=email,
            to="test@example.com",
            subject="Test Email from Zara Assistant",
            body="Hello! This is a test email from Zara Assistant using VIT email credentials.",
            provider=provider,
            tone="friendly",
            dry_run=True
        )
        
        if test_result['success']:
            print("✅ Email composition test passed!")
            print(f"Details: {test_result['details']}")
        else:
            print(f"❌ Email composition failed: {test_result['error']}")
            return
        
        # Test through tools module
        print("\n🛠️ Testing through tools module...")
        from zara.tools import send_email
        
        # We'll modify the function call to include provider
        tools_result = send_email(
            to="recipient@example.com",
            subject="Test from Tools Module",
            body="This is a test from the tools module.",
            sender=email
        )
        
        print(f"Tools module result: {tools_result}")
        
        # Interactive sending option
        print("\n🚀 Setup Complete!")
        print("="*50)
        print("Your VIT email is now configured and ready to use!")
        print("\nTo send emails, you can:")
        print("1. Run: python main.py")
        print("   Then say: 'send an email to someone@example.com'")
        print("\n2. Use Python directly:")
        print(f"   from zara.tools import send_email")
        print(f"   send_email(to='recipient@gmail.com', subject='Hello', body='Test message')")
        
        # Offer to send a real test email
        user_input = input("\n❓ Would you like to send a real test email? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            recipient = input("Enter recipient email address: ").strip()
            if recipient:
                send_real_test_email(email_sender, email, recipient, provider)
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

def send_real_test_email(email_sender, sender_email, recipient, provider):
    """Send a real test email."""
    print(f"\n📤 Sending real test email to {recipient}...")
    
    try:
        result = email_sender.send_email(
            sender_email=sender_email,
            to=recipient,
            subject="Test Email from Zara Assistant",
            body="Hello! This is a test email from Zara Assistant. If you receive this, the email functionality is working correctly!",
            provider=provider,
            tone="friendly",
            dry_run=False
        )
        
        if result['success']:
            print(f"✅ Email sent successfully to {recipient}!")
            print("Check the recipient's inbox.")
        else:
            print(f"❌ Failed to send email: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    setup_and_test_vit_email() 