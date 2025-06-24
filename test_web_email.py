# -*- coding: utf-8 -*-
"""
Test script for Web Email Automation

This script demonstrates how to use Zara's new web email automation feature.
"""

import sys
import os

# Add the project root to path so we can import zara modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_web_email_basic():
    """Test basic web email functionality."""
    print("🧪 Testing Web Email Automation")
    print("=" * 50)
    
    try:
        from zara.email_web_automation import WebEmailAutomation
        
        # Create web email instance (without voice for testing)
        web_email = WebEmailAutomation(voice_interface=None)
        
        print("✅ Web email automation loaded successfully!")
        
        # Test with predefined content (to avoid interactive prompts in test)
        test_email = "srivallabhkakaral@gmail.com"
        test_subject = "Test from Zara Web Automation"
        test_body = "This is a test email sent using Zara's new web automation feature! 🚀\n\nIt opens Gmail and fills in the content automatically."
        
        print(f"\n📧 Preparing to send test email:")
        print(f"To: {test_email}")
        print(f"Subject: {test_subject}")
        print(f"Body: {test_body[:50]}...")
        
        # Ask user if they want to proceed
        proceed = input("\nDo you want to open Gmail with this test email? (yes/no): ").lower().strip()
        
        if proceed in ['yes', 'y']:
            # Send the email using web automation
            result = web_email.send_email_web(
                to_email=test_email,
                subject=test_subject,
                body=test_body
            )
            
            print(f"\n📬 Result: {result}")
            
        else:
            print("❌ Test cancelled by user")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try installing missing dependencies: pip install pyautogui pyperclip")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_zara_tools_integration():
    """Test integration with Zara's tools module."""
    print("\n🔧 Testing Zara Tools Integration")
    print("=" * 50)
    
    try:
        from zara.tools import send_email
        
        print("✅ Zara tools module loaded successfully!")
        
        # Test the integrated send_email function
        print("\n📧 Testing send_email function...")
        
        # This will trigger the interactive web email flow
        result = send_email()
        
        print(f"\n📬 Result: {result}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_voice_commands():
    """Test voice command integration (if voice module available)."""
    print("\n🎤 Testing Voice Command Integration")
    print("=" * 50)
    
    try:
        from zara.email_web_automation import handle_send_email_command
        
        print("✅ Voice command handlers loaded successfully!")
        print("💡 Note: Voice interface testing requires microphone and TTS setup")
        
        # Test without actual voice interface for now
        result = handle_send_email_command(voice_interface=None)
        print(f"\n📬 Voice command result: {result}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_feature_summary():
    """Show a summary of the new web email features."""
    print("\n🌟 Web Email Automation Features")
    print("=" * 50)
    
    features = [
        "✅ Opens Gmail automatically in your default browser",
        "✅ Pre-fills recipient, subject, and body content",
        "✅ Works with voice commands (say recipient email address)",
        "✅ Handles email address cleanup (converts 'at' to '@', 'dot' to '.')",
        "✅ Applies personality tones (friendly, professional, formal)",
        "✅ Safety confirmation before opening Gmail",
        "✅ Fallback to clipboard if URL pre-filling doesn't work",
        "✅ No SMTP authentication issues",
        "✅ Works with any email provider (Gmail, Outlook, Yahoo, etc.)",
        "✅ Integrates seamlessly with Zara's existing tool system"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n💬 Usage Examples:")
    print("- Voice: 'Hey Zara, send an email'")
    print("- Code: send_email()")
    print("- Code: send_email('john@example.com', 'Hello', 'How are you?')")

def main():
    """Main test function."""
    print("🤖 Zara Web Email Automation Test Suite")
    print("=" * 60)
    
    # Show feature summary first
    show_feature_summary()
    
    # Run tests
    test_web_email_basic()
    
    # Ask if user wants to test more features
    test_more = input("\nDo you want to test Zara tools integration? (yes/no): ").lower().strip()
    if test_more in ['yes', 'y']:
        test_zara_tools_integration()
    
    test_voice = input("\nDo you want to test voice command handlers? (yes/no): ").lower().strip()
    if test_voice in ['yes', 'y']:
        test_voice_commands()
    
    print("\n🎉 Test suite completed!")
    print("💡 Now you can use 'send an email' voice commands or call send_email() in code")

if __name__ == "__main__":
    main() 