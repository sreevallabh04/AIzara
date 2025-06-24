# -*- coding: utf-8 -*-
"""
Contacts Setup and Test Script for Zara Assistant

This script helps you set up your contacts and test the new contact-based email functionality.
"""

import sys
import os

# Add the project root to path so we can import zara modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_sample_contacts():
    """Set up sample contacts for demonstration."""
    print("📝 Setting up sample contacts...")
    
    try:
        from zara.contacts import get_contacts_manager
        
        contacts = get_contacts_manager()
        
        # Sample contacts - you can customize these with real information
        sample_contacts = [
            {"name": "Mom", "phone": "+1-555-0101", "email": "mom@family.com"},
            {"name": "Dad", "phone": "+1-555-0102", "email": "dad@family.com"},
            {"name": "John", "phone": "+1-555-0201", "email": "john.doe@gmail.com"},
            {"name": "Sarah", "phone": "+1-555-0202", "email": "sarah.smith@gmail.com"},
            {"name": "Mike", "phone": "+1-555-0203", "email": "mike.jones@gmail.com"},
            {"name": "Emily", "phone": "+1-555-0204", "email": "emily.davis@gmail.com"},
            {"name": "Professor Smith", "phone": "+1-555-0301", "email": "prof.smith@university.edu"},
            {"name": "Boss", "phone": "+1-555-0401", "email": "boss@company.com"}
        ]
        
        added_count = 0
        for contact_data in sample_contacts:
            if contacts.add_contact(
                contact_data["name"],
                contact_data["phone"],
                contact_data["email"]
            ):
                added_count += 1
                print(f"✅ Added: {contact_data['name']}")
        
        print(f"\n🎉 Successfully added {added_count} sample contacts!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up contacts: {e}")
        return False

def interactive_add_real_contacts():
    """Interactive function to add your real contacts."""
    print("\n📞 Add Your Real Contacts")
    print("=" * 50)
    print("Let's add your friends and family members!")
    print("(Press Enter to skip phone/email if not available)")
    
    try:
        from zara.contacts import get_contacts_manager
        
        contacts = get_contacts_manager()
        added_count = 0
        
        while True:
            print(f"\n--- Contact #{added_count + 1} ---")
            
            name = input("Enter contact name (or 'done' to finish): ").strip()
            if name.lower() in ['done', 'quit', 'exit']:
                break
            
            if not name:
                print("❌ Name cannot be empty. Please try again.")
                continue
            
            phone = input("Enter phone number (optional): ").strip()
            email = input("Enter email address (optional): ").strip()
            
            if contacts.add_contact(name, phone, email):
                print(f"✅ Added: {name}")
                added_count += 1
            else:
                print(f"❌ Failed to add: {name}")
        
        print(f"\n🎉 Successfully added {added_count} of your contacts!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding contacts: {e}")
        return False

def show_all_contacts():
    """Display all contacts in the system."""
    print("\n📋 Your Current Contacts")
    print("=" * 50)
    
    try:
        from zara.contacts import get_contacts_manager
        
        contacts = get_contacts_manager()
        all_contacts = contacts.get_all_contacts()
        
        if not all_contacts:
            print("📭 No contacts found. Add some contacts first!")
            return
        
        for i, contact in enumerate(all_contacts, 1):
            print(f"{i}. 👤 {contact.name}")
            if contact.phone:
                print(f"   📞 {contact.phone}")
            if contact.email:
                print(f"   📧 {contact.email}")
            print()
        
        print(f"Total contacts: {len(all_contacts)}")
        
    except Exception as e:
        print(f"❌ Error showing contacts: {e}")

def test_contact_email_functionality():
    """Test the contact-based email functionality."""
    print("\n🧪 Testing Contact-Based Email")
    print("=" * 50)
    
    try:
        from zara.contacts import get_contacts_manager, get_contacts_email_integration
        
        contacts = get_contacts_manager()
        email_integration = get_contacts_email_integration()
        
        # Get all contacts
        all_contacts = contacts.get_all_contacts()
        
        if not all_contacts:
            print("❌ No contacts found. Please add some contacts first.")
            return
        
        # Show available contacts
        print("Available contacts for email testing:")
        for i, contact in enumerate(all_contacts, 1):
            status = "✅" if contact.email else "❌ (no email)"
            print(f"{i}. {contact.name} {status}")
        
        print("\nChoose a contact to send a test email:")
        choice = input("Enter contact name: ").strip()
        
        if not choice:
            print("❌ No contact selected.")
            return
        
        # Find the contact
        contact = contacts.get_contact(choice)
        if not contact:
            print(f"❌ Contact '{choice}' not found.")
            return
        
        if not contact.email:
            print(f"❌ No email address found for {contact.name}")
            return
        
        print(f"\n📧 Testing email to {contact.name} ({contact.email})")
        
        # Test the email functionality
        test_subject = "Test Email from Zara Assistant"
        test_body = f"Hi {contact.name}!\n\nThis is a test email from Zara Assistant's new contact-based email feature.\n\nBest regards,\nZara 🤖"
        
        print("Email content preview:")
        print(f"To: {contact.email}")
        print(f"Subject: {test_subject}")
        print(f"Body: {test_body[:100]}...")
        
        proceed = input("\nSend this test email? (yes/no): ").lower().strip()
        
        if proceed in ['yes', 'y']:
            result = email_integration.send_email_to_contact(
                contact.name, 
                test_subject, 
                test_body
            )
            print(f"\n📬 Result: {result}")
        else:
            print("❌ Test cancelled.")
        
    except Exception as e:
        print(f"❌ Error testing email functionality: {e}")

def test_voice_commands():
    """Show examples of voice commands that now work."""
    print("\n🎤 Voice Commands You Can Now Use")
    print("=" * 50)
    
    commands = [
        "send an email to Mom",
        "email John about meeting",
        "compose an email to Sarah saying hello",
        "write an email to Dad about weekend plans",
        "add contact Alice phone 123-456-7890 email alice@email.com",
        "show all contacts",
        "list contacts",
        "find contact John"
    ]
    
    print("Now that you have contacts set up, you can use these voice commands:")
    print()
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. 🗣️ \"{command}\"")
    
    print("\n💡 Tips:")
    print("- Contact names are fuzzy-matched (e.g., 'John' will match 'John Doe')")
    print("- You can include subject and message in the voice command")
    print("- Gmail will open automatically with the email pre-filled")
    print("- No need to remember email addresses anymore!")

def test_natural_language_parsing():
    """Test the natural language parsing for email commands."""
    print("\n🧠 Testing Natural Language Parsing")
    print("=" * 50)
    
    try:
        from zara.contacts import ContactsEmailIntegration
        
        integration = ContactsEmailIntegration()
        
        test_commands = [
            "send an email to John",
            "email Mom about dinner plans",
            "compose an email to Sarah saying I'll be late",
            "write an email to Dad about vacation saying we should plan a trip",
            "send email to Professor Smith about assignment"
        ]
        
        print("Testing command parsing:")
        print()
        
        for command in test_commands:
            contact_name, subject, body = integration.parse_email_command(command)
            print(f"📝 Command: \"{command}\"")
            print(f"   👤 Contact: {contact_name}")
            print(f"   📋 Subject: {subject}")
            print(f"   💬 Body: {body}")
            print()
        
    except Exception as e:
        print(f"❌ Error testing parsing: {e}")

def main():
    """Main setup and test function."""
    print("🤖 Zara Assistant - Contacts Setup & Test")
    print("=" * 60)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. 📝 Set up sample contacts (for testing)")
        print("2. 👥 Add your real contacts")
        print("3. 📋 Show all contacts")
        print("4. 🧪 Test contact-based email")
        print("5. 🎤 Show voice command examples")
        print("6. 🧠 Test natural language parsing")
        print("0. ❌ Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "1":
            setup_sample_contacts()
        elif choice == "2":
            interactive_add_real_contacts()
        elif choice == "3":
            show_all_contacts()
        elif choice == "4":
            test_contact_email_functionality()
        elif choice == "5":
            test_voice_commands()
        elif choice == "6":
            test_natural_language_parsing()
        elif choice == "0":
            print("\n👋 Goodbye! Your contacts are ready for use with Zara.")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 