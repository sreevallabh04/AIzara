# -*- coding: utf-8 -*-
"""
Test Contact-Based Email for Zara Assistant

This script demonstrates how the new contact-based email system works.
"""

import sys
import os

# Add the project root to path so we can import zara modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_send_email_to_amma():
    """Test sending an email to Amma using the contact system."""
    print("🧪 Testing Contact-Based Email: Send to Amma")
    print("=" * 50)
    
    try:
        from zara.contacts import get_contacts_email_integration
        
        # Get the email integration
        email_integration = get_contacts_email_integration()
        
        # Test data
        contact_name = "Amma"
        subject = "Test from Zara Assistant"
        body = "Hi Amma!\n\nThis is a test email from Zara's new contact-based email system. It automatically found your email address (sudharanivaidya@gmail.com) from my contacts!\n\nLove,\nZara 🤖"
        
        print(f"📧 Preparing email to: {contact_name}")
        print(f"📋 Subject: {subject}")
        print(f"💬 Message: {body[:50]}...")
        
        # Ask user if they want to proceed
        proceed = input("\nWould you like to test sending this email to Amma? (yes/no): ").lower().strip()
        
        if proceed in ['yes', 'y']:
            # This will open Gmail with the email pre-filled
            result = email_integration.send_email_to_contact(
                contact_name, 
                subject, 
                body
            )
            print(f"\n📬 Result: {result}")
        else:
            print("❌ Test cancelled by user")
            
    except Exception as e:
        print(f"❌ Error testing email: {e}")

def test_voice_command_parsing():
    """Test how voice commands are parsed."""
    print("\n🧠 Testing Voice Command Parsing")
    print("=" * 50)
    
    try:
        from zara.contacts import ContactsEmailIntegration
        
        integration = ContactsEmailIntegration()
        
        # Test voice commands with your actual contacts
        test_commands = [
            "send an email to Amma",
            "email Shivani about weekend plans",
            "compose an email to Sahith saying how are you doing?",
            "write an email to Raazi about meeting saying let's meet tomorrow",
            "send email to Hansika about project"
        ]
        
        print("Testing how Zara would parse these voice commands:")
        print()
        
        for command in test_commands:
            contact_name, subject, body = integration.parse_email_command(command)
            print(f"🗣️ You say: \"{command}\"")
            print(f"   👤 Zara finds contact: {contact_name}")
            print(f"   📋 Subject: {subject}")
            print(f"   💬 Body: {body}")
            print()
        
    except Exception as e:
        print(f"❌ Error testing parsing: {e}")

def simulate_agent_command():
    """Simulate how the agent would handle a voice command."""
    print("\n🤖 Simulating Agent Voice Command")
    print("=" * 50)
    
    try:
        # Import the tools that the agent would use
        from zara.tools import send_email_to_contact
        
        print("Simulating: 'Send an email to Shivani'")
        print()
        
        # This is what happens when you say "send an email to Shivani"
        contact_name = "Shivani"
        print(f"🔍 Zara looks up contact: {contact_name}")
        print("📧 Found: dathashivani09@gmail.com")
        print("🌐 Opening Gmail with pre-filled email...")
        
        # Ask user if they want to test this
        proceed = input("Test this functionality? (yes/no): ").lower().strip()
        
        if proceed in ['yes', 'y']:
            # This will open Gmail automatically
            result = send_email_to_contact(contact_name)
            print(f"\n📬 Result: {result}")
        else:
            print("❌ Test cancelled")
            
    except Exception as e:
        print(f"❌ Error simulating command: {e}")

def main():
    """Main test function."""
    print("🤖 Zara Contact-Based Email Test")
    print("=" * 60)
    print("Your contacts are now stored in Zara's database!")
    print("This means you can use voice commands like:")
    print("• 'Send an email to Amma'")
    print("• 'Email Shivani about dinner'")
    print("• 'Compose an email to Sahith saying hello'")
    print()
    
    while True:
        print("\nWhat would you like to test?")
        print("1. 🧪 Test sending email to Amma")
        print("2. 🧠 Test voice command parsing")
        print("3. 🤖 Simulate agent voice command")
        print("0. ❌ Exit")
        
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == "1":
            test_send_email_to_amma()
        elif choice == "2":
            test_voice_command_parsing()
        elif choice == "3":
            simulate_agent_command()
        elif choice == "0":
            print("\n👋 Testing complete! Your contact-based email system is ready!")
            print("Now you can use voice commands with Zara to send emails by name!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 