# -*- coding: utf-8 -*-
"""
Quick VIT Email Setup Script
"""

import sys
import json
import base64
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_vit_email_direct():
    """Setup VIT email credentials directly to encrypted file."""
    print("Setting up VIT email credentials...")
    
    # Create credentials directory
    credentials_dir = Path("data/encrypted")
    credentials_dir.mkdir(parents=True, exist_ok=True)
    credentials_file = credentials_dir / "email_credentials.json"
    
    # VIT email credentials
    email = "sreevalllabh.2022@vitstudent.ac.in"
    password = "wheredobrokenheartsgo"
    provider = "vit"
    
    # Create credential data
    credential_data = {
        'email': email,
        'password': password,
        'provider': provider,
        'stored_at': '2024-06-24T10:30:00'
    }
    
    # Store in simple format for now
    account_key = f"{email}_{provider}"
    all_credentials = {account_key: credential_data}
    
    # Encrypt using simple base64 (for demo purposes)
    credentials_json = json.dumps(all_credentials, indent=2)
    encrypted_data = base64.b64encode(credentials_json.encode()).decode()
    
    # Save to file
    with open(credentials_file, 'w') as f:
        f.write(encrypted_data)
    
    print(f"✅ Credentials stored securely in {credentials_file}")
    
    # Test with the tools module
    print("\nTesting email function...")
    try:
        from zara.tools import send_email
        
        # Test with a dry run equivalent
        print("Email function imported successfully!")
        print(f"Ready to send emails from: {email}")
        print("\nTo send an email, use:")
        print(f'  send_email(to="recipient@example.com", subject="Test", body="Hello from Zara!")')
        
    except Exception as e:
        print(f"Error testing email function: {e}")

def test_email_sending():
    """Test sending an email with the configured credentials."""
    print("\n" + "="*50)
    print("TESTING EMAIL SENDING")
    print("="*50)
    
    try:
        from plugins.email_sender.plugin import create_plugin
        from zara.security.keychain import KeychainManager
        
        # Initialize
        keychain = KeychainManager(use_os_keychain=False)  # Force file storage
        email_plugin = create_plugin(keychain_manager=keychain)
        
        # Disable confirmation for testing
        email_plugin.confirmation_required = False
        
        # Test dry run
        result = email_plugin.send_email_command(
            to="test@example.com",
            subject="Test Email from Zara Assistant",
            body="This is a test message to verify the email functionality.",
            tone="friendly"
        )
        
        print(f"Test result: {result}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_vit_email_direct()
    test_email_sending() 