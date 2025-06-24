# -*- coding: utf-8 -*-
"""
One-time setup script for VIT email credentials
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from plugins.email_sender.plugin import create_plugin
from zara.security.keychain import KeychainManager

def setup_vit_email():
    """Setup VIT email credentials securely."""
    print("Setting up VIT email credentials...")
    
    # Initialize components
    keychain = KeychainManager()
    email_plugin = create_plugin(keychain_manager=keychain)
    
    # VIT email credentials
    email = "sreevalllabh.2022@vitstudent.ac.in"
    password = "wheredobrokenheartsgo"
    provider = "outlook"  # VIT uses Microsoft Exchange
    
    # Store credentials securely
    result = email_plugin.setup_credentials_command(
        email=email,
        password=password,
        provider=provider
    )
    
    print(f"Setup result: {result}")
    
    # Test the credentials with a dry run
    print("\nTesting credentials with dry run...")
    test_result = email_plugin.email_sender.send_email(
        sender_email=email,
        to="test@example.com",
        subject="Test from Zara Assistant",
        body="This is a test email to verify credentials work.",
        provider=provider,
        dry_run=True
    )
    
    if test_result['success']:
        print("✅ Credentials setup and validated successfully!")
        print("You can now send emails using Zara Assistant.")
        print("\nTo send an email, run:")
        print("  python main.py")
        print("  Then say: 'send an email to someone@example.com'")
    else:
        print(f"❌ Credential validation failed: {test_result['error']}")
    
    # Clean up - remove this script after use for security
    print(f"\n🔒 For security, consider deleting this setup script after use:")
    print(f"  del {__file__}")

if __name__ == "__main__":
    setup_vit_email() 