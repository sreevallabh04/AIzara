# -*- coding: utf-8 -*-
"""
Email Plugin Test Script for Zara Assistant
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from plugins.email_sender.plugin import create_plugin, EmailConfig
    from zara.security.keychain import KeychainManager
    print("Successfully imported email plugin components")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_email_plugin():
    """Basic test of the email plugin."""
    print("Testing Email Plugin...")
    
    try:
        # Initialize components
        keychain = KeychainManager()
        email_plugin = create_plugin(keychain_manager=keychain)
        print("Email plugin initialized successfully")
        
        # Test keychain info
        info = keychain.get_keychain_info()
        print(f"Platform: {info['platform']}")
        print(f"OS Keychain Available: {info['os_keychain_available']}")
        print(f"File Storage Available: {info['file_storage_available']}")
        
        # Test email validation
        test_emails = ["user@example.com", "invalid-email", "test@domain.org"]
        print("\nTesting email validation:")
        for email in test_emails:
            is_valid = email_plugin.email_sender.validate_email_address(email)
            print(f"Email {email}: {'Valid' if is_valid else 'Invalid'}")
        
        # Test content sanitization
        print("\nTesting content sanitization:")
        test_content = "<script>alert('xss')</script>Hello World"
        sanitized = email_plugin.email_sender.sanitize_email_content(test_content)
        print(f"Original: {test_content}")
        print(f"Sanitized: {sanitized}")
        
        # Test personality tones
        print("\nTesting personality tones:")
        test_body = "I wanted to update you on the project status."
        tones = ['friendly', 'professional', 'formal']
        
        for tone in tones:
            modified_body = email_plugin.email_sender.apply_personality_tone(test_body, tone)
            print(f"{tone.upper()}: {modified_body}")
        
        print("\nEmail plugin test completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_plugin() 