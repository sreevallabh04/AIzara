# -*- coding: utf-8 -*-
"""
Add Real Contacts for Zara Assistant

This script adds your specific contacts to the system.
"""

import sys
import os

# Add the project root to path so we can import zara modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_real_contacts():
    """Add your real contacts to the system."""
    print("📝 Adding your real contacts...")
    
    try:
        from zara.contacts import get_contacts_manager
        
        contacts = get_contacts_manager()
        
        # Your real contacts
        real_contacts = [
            {"name": "Amma", "phone": "9849854892", "email": "sudharanivaidya@gmail.com"},
            {"name": "Shivani", "phone": "6303270295", "email": "dathashivani09@gmail.com"},
            {"name": "Sahith", "phone": "8008892225", "email": "sahithraolingampally@gmail.com"},
            {"name": "Raazi", "phone": "8722019159", "email": "raazi.faisal@gmail.com"},  # Fixed phone number
            {"name": "Hansika", "phone": "9014679963", "email": "kallurihansikareddy5@gmail.com"},
            {"name": "Soham", "phone": "9959200325", "email": "sohamshashidhar@gmail.com"},
            {"name": "Shahzil", "phone": "9455759786", "email": "theshahzil@gmail.com"}
        ]
        
        added_count = 0
        for contact_data in real_contacts:
            if contacts.add_contact(
                contact_data["name"],
                contact_data["phone"],
                contact_data["email"]
            ):
                added_count += 1
                print(f"✅ Added: {contact_data['name']} - {contact_data['phone']} - {contact_data['email']}")
        
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
            print("📭 No contacts found.")
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

def test_email_commands():
    """Show examples of voice commands you can now use."""
    print("\n🎤 Voice Commands You Can Now Use")
    print("=" * 60)
    
    commands = [
        "send an email to Amma",
        "email Shivani about weekend plans",
        "compose an email to Sahith saying hello",
        "write an email to Raazi about meeting",
        "send email to Hansika about project",
        "email Soham about dinner",
        "compose an email to Shahzil saying thanks"
    ]
    
    print("Now you can use these voice commands:")
    print()
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. 🗣️ \"{command}\"")
    
    print("\n💡 How it works:")
    print("1. You say: 'send an email to Amma'")
    print("2. Zara will automatically use sudharanivaidya@gmail.com")
    print("3. Gmail opens with the email pre-filled")
    print("4. You just review and send!")
    
    print("\n🎯 Advanced Examples:")
    print("🗣️ \"email Amma about dinner saying let's meet at 7 PM\"")
    print("   → Will pre-fill subject: 'dinner' and body: 'let's meet at 7 PM'")
    print()
    print("🗣️ \"send email to Shivani about project update\"")
    print("   → Will pre-fill subject: 'project update'")

def main():
    """Main function."""
    print("🤖 Adding Your Real Contacts to Zara Assistant")
    print("=" * 60)
    
    # Add your contacts
    add_real_contacts()
    
    # Show all contacts
    show_all_contacts()
    
    # Show example commands
    test_email_commands()
    
    print("\n✨ Setup Complete!")
    print("Your contacts are now ready for use with Zara's email automation!")

if __name__ == "__main__":
    main() 