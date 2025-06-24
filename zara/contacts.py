# -*- coding: utf-8 -*-
"""
Contacts Management System for Zara Assistant

This system stores and manages contacts (friends, family) with their details
and integrates with email automation for seamless communication.
"""

import json
import os
import sqlite3
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class Contact:
    """Represents a single contact with name, phone, and email."""
    
    def __init__(self, name: str, phone: str = "", email: str = ""):
        self.name = name.strip().title()
        self.phone = phone.strip()
        self.email = email.strip().lower()
        
    def to_dict(self) -> Dict[str, str]:
        """Convert contact to dictionary."""
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Contact':
        """Create contact from dictionary."""
        return cls(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", "")
        )
    
    def __str__(self) -> str:
        return f"{self.name} - Phone: {self.phone}, Email: {self.email}"

class ContactsManager:
    """Manages contacts storage and retrieval."""
    
    def __init__(self, db_path: str = "data/zara_assistant.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the contacts database table."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        phone TEXT,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("Contacts database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize contacts database: {e}")
            raise
    
    def add_contact(self, name: str, phone: str = "", email: str = "") -> bool:
        """Add a new contact or update existing one."""
        try:
            contact = Contact(name, phone, email)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if contact exists
                cursor.execute("SELECT id FROM contacts WHERE name = ?", (contact.name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing contact
                    cursor.execute("""
                        UPDATE contacts 
                        SET phone = ?, email = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE name = ?
                    """, (contact.phone, contact.email, contact.name))
                    logger.info(f"Updated contact: {contact.name}")
                else:
                    # Insert new contact
                    cursor.execute("""
                        INSERT INTO contacts (name, phone, email)
                        VALUES (?, ?, ?)
                    """, (contact.name, contact.phone, contact.email))
                    logger.info(f"Added new contact: {contact.name}")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to add contact {name}: {e}")
            return False
    
    def get_contact(self, name: str) -> Optional[Contact]:
        """Get a contact by name (case-insensitive, fuzzy matching)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First try exact match (case-insensitive)
                cursor.execute(
                    "SELECT name, phone, email FROM contacts WHERE LOWER(name) = LOWER(?)",
                    (name.strip(),)
                )
                result = cursor.fetchone()
                
                if result:
                    return Contact(result[0], result[1], result[2])
                
                # Try partial match if exact match fails
                cursor.execute(
                    "SELECT name, phone, email FROM contacts WHERE LOWER(name) LIKE LOWER(?)",
                    (f"%{name.strip()}%",)
                )
                results = cursor.fetchall()
                
                if results:
                    # If multiple matches, prefer the shortest name (most likely match)
                    best_match = min(results, key=lambda x: len(x[0]))
                    return Contact(best_match[0], best_match[1], best_match[2])
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get contact {name}: {e}")
            return None
    
    def get_all_contacts(self) -> List[Contact]:
        """Get all contacts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, phone, email FROM contacts ORDER BY name")
                results = cursor.fetchall()
                
                return [Contact(row[0], row[1], row[2]) for row in results]
                
        except Exception as e:
            logger.error(f"Failed to get all contacts: {e}")
            return []
    
    def delete_contact(self, name: str) -> bool:
        """Delete a contact by name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM contacts WHERE LOWER(name) = LOWER(?)", (name.strip(),))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Deleted contact: {name}")
                    return True
                else:
                    logger.warning(f"Contact not found for deletion: {name}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to delete contact {name}: {e}")
            return False
    
    def search_contacts(self, query: str) -> List[Contact]:
        """Search contacts by name, phone, or email."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                search_pattern = f"%{query.strip()}%"
                
                cursor.execute("""
                    SELECT name, phone, email FROM contacts 
                    WHERE LOWER(name) LIKE LOWER(?) 
                       OR LOWER(phone) LIKE LOWER(?) 
                       OR LOWER(email) LIKE LOWER(?)
                    ORDER BY name
                """, (search_pattern, search_pattern, search_pattern))
                
                results = cursor.fetchall()
                return [Contact(row[0], row[1], row[2]) for row in results]
                
        except Exception as e:
            logger.error(f"Failed to search contacts: {e}")
            return []
    
    def bulk_add_contacts(self, contacts_data: List[Dict[str, str]]) -> int:
        """Add multiple contacts at once. Returns number of contacts added."""
        added_count = 0
        for contact_data in contacts_data:
            if self.add_contact(
                contact_data.get("name", ""),
                contact_data.get("phone", ""),
                contact_data.get("email", "")
            ):
                added_count += 1
        return added_count

class ContactsEmailIntegration:
    """Integrates contacts with email automation system."""
    
    def __init__(self, contacts_manager: ContactsManager = None):
        self.contacts = contacts_manager or ContactsManager()
    
    def send_email_to_contact(self, contact_name: str, subject: str = None, body: str = None, **kwargs):
        """Send email to a contact by name using web automation."""
        try:
            # Find the contact
            contact = self.contacts.get_contact(contact_name)
            
            if not contact:
                return f"❌ Contact '{contact_name}' not found in your address book"
            
            if not contact.email:
                return f"❌ No email address found for {contact.name}"
            
            # Import web email automation
            from zara.email_web_automation import send_email_web_integrated
            
            # Send email using the contact's email
            result = send_email_web_integrated(
                to=contact.email,
                subject=subject,
                body=body,
                **kwargs
            )
            
            # Add context about the contact
            if "Gmail opened" in result:
                return f"📧 {result} for {contact.name} ({contact.email})"
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to send email to contact {contact_name}: {e}")
            return f"❌ Error sending email to {contact_name}: {str(e)}"
    
    def parse_email_command(self, message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse email command from natural language.
        Returns (contact_name, subject, body) tuple.
        """
        # Patterns for "send email to [name]"
        patterns = [
            r"send\s+(?:an?\s+)?email\s+to\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$",
            r"email\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$",
            r"compose\s+(?:an?\s+)?email\s+to\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$",
            r"write\s+(?:an?\s+)?email\s+to\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.strip(), re.IGNORECASE)
            if match:
                contact_name = match.group(1).strip()
                subject = match.group(2).strip() if match.group(2) else None
                body = match.group(3).strip() if match.group(3) else None
                
                return contact_name, subject, body
        
        return None, None, None

# Contact management utility functions
def add_sample_contacts():
    """Add some sample contacts for demonstration."""
    contacts = ContactsManager()
    
    sample_contacts = [
        {"name": "Mom", "phone": "+1-555-0101", "email": "mom@family.com"},
        {"name": "Dad", "phone": "+1-555-0102", "email": "dad@family.com"},
        {"name": "John", "phone": "+1-555-0201", "email": "john.doe@email.com"},
        {"name": "Sarah", "phone": "+1-555-0202", "email": "sarah.smith@email.com"},
        {"name": "Mike", "phone": "+1-555-0203", "email": "mike.jones@email.com"},
        {"name": "Emily", "phone": "+1-555-0204", "email": "emily.davis@email.com"},
        {"name": "Professor Smith", "phone": "+1-555-0301", "email": "prof.smith@university.edu"},
        {"name": "Boss", "phone": "+1-555-0401", "email": "boss@company.com"}
    ]
    
    added = contacts.bulk_add_contacts(sample_contacts)
    return f"Added {added} sample contacts"

def interactive_add_contact():
    """Interactive function to add a contact."""
    print("📝 Add New Contact")
    print("=" * 30)
    
    name = input("Enter contact name: ").strip()
    if not name:
        return "❌ Name is required"
    
    phone = input("Enter phone number (optional): ").strip()
    email = input("Enter email address (optional): ").strip()
    
    contacts = ContactsManager()
    if contacts.add_contact(name, phone, email):
        return f"✅ Contact '{name}' added successfully"
    else:
        return f"❌ Failed to add contact '{name}'"

def list_all_contacts():
    """List all contacts."""
    contacts = ContactsManager()
    all_contacts = contacts.get_all_contacts()
    
    if not all_contacts:
        return "📭 No contacts found"
    
    result = "📋 Your Contacts:\n"
    result += "=" * 40 + "\n"
    
    for contact in all_contacts:
        result += f"👤 {contact.name}\n"
        if contact.phone:
            result += f"   📞 {contact.phone}\n"
        if contact.email:
            result += f"   📧 {contact.email}\n"
        result += "\n"
    
    return result

# Global contacts manager instance
_contacts_manager = None

def get_contacts_manager() -> ContactsManager:
    """Get the global contacts manager instance."""
    global _contacts_manager
    if _contacts_manager is None:
        _contacts_manager = ContactsManager()
    return _contacts_manager

def get_contacts_email_integration() -> ContactsEmailIntegration:
    """Get the contacts email integration instance."""
    return ContactsEmailIntegration(get_contacts_manager()) 