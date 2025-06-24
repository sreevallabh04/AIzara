# -*- coding: utf-8 -*-
"""
Web Automation Email System for Zara Assistant

This system opens Gmail in a web browser and automatically fills in email content,
avoiding SMTP authentication issues while providing a seamless user experience.
"""

import webbrowser
import time
import pyautogui
import pyperclip
from urllib.parse import quote
import logging
import asyncio

logger = logging.getLogger(__name__)

class WebEmailAutomation:
    """
    Web-based email automation that opens Gmail and fills content automatically.
    """
    
    def __init__(self, voice_interface=None):
        self.voice = voice_interface
        self.default_email = "srivallabhkakaral@gmail.com"
        
        # Configure pyautogui for safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0  # 1 second pause between actions
    
    def send_email_web(self, to_email=None, subject=None, body=None, **kwargs):
        """
        Main email sending function that opens Gmail and automates content entry.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
        """
        try:
            # Get email details interactively if not provided
            if not to_email:
                to_email = self._get_recipient_email()
            
            if not subject:
                subject = self._get_email_subject()
            
            if not body:
                body = self._get_email_body()
            
            # Apply personality tone if available
            if hasattr(self, 'personality') and self.personality:
                tone = kwargs.get('tone', 'friendly')
                body = self._apply_personality_tone(body, tone)
            
            # Confirm with user before proceeding
            if not self._confirm_email_send(to_email, subject, body):
                return "Email sending cancelled by user"
            
            # Open Gmail and automate email composition
            success = self._automate_gmail_compose(to_email, subject, body)
            
            if success:
                return f"✅ Gmail opened and email content filled for {to_email}"
            else:
                return "❌ Failed to automate Gmail email composition"
                
        except Exception as e:
            logger.error(f"Web email automation error: {e}")
            return f"Error in web email automation: {str(e)}"
    
    def _get_recipient_email(self):
        """Get recipient email address from user."""
        if self.voice and hasattr(self.voice, 'speak') and hasattr(self.voice, 'listen'):
            # Voice interaction
            self.voice.speak("Who would you like to send the email to? Please say the email address.")
            
            # Listen for email address
            for attempt in range(3):  # Try up to 3 times
                # Handle async listen method properly
                if asyncio.iscoroutinefunction(self.voice.listen):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        recipient = loop.run_until_complete(self.voice.listen())
                    finally:
                        loop.close()
                else:
                    recipient = self.voice.listen()
                    
                if recipient and '@' in recipient:
                    # Clean up the spoken email (replace "at" with "@", "dot" with ".")
                    cleaned_email = self._clean_spoken_email(recipient)
                    
                    # Confirm the email address
                    self.voice.speak(f"Did you say {cleaned_email}? Say yes to confirm or no to try again.")
                    
                    # Handle async confirmation
                    if asyncio.iscoroutinefunction(self.voice.listen):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            confirmation = loop.run_until_complete(self.voice.listen())
                        finally:
                            loop.close()
                    else:
                        confirmation = self.voice.listen()
                    
                    if confirmation and 'yes' in confirmation.lower():
                        return cleaned_email
                
                self.voice.speak("I didn't catch that clearly. Please say the email address again.")
            
            # Fallback to text input
            self.voice.speak("Let me get the email address through text input.")
        
        # Text input fallback
        return input("Enter recipient email address: ").strip()
    
    def _get_email_subject(self):
        """Get email subject from user."""
        if self.voice and hasattr(self.voice, 'speak') and hasattr(self.voice, 'listen'):
            self.voice.speak("What's the subject of the email?")
            
            # Handle async listen method properly
            if asyncio.iscoroutinefunction(self.voice.listen):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    subject = loop.run_until_complete(self.voice.listen())
                finally:
                    loop.close()
            else:
                subject = self.voice.listen()
                
            if subject:
                # Confirm subject
                self.voice.speak(f"Subject: {subject}. Is that correct? Say yes to confirm.")
                
                # Handle async confirmation
                if asyncio.iscoroutinefunction(self.voice.listen):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        confirmation = loop.run_until_complete(self.voice.listen())
                    finally:
                        loop.close()
                else:
                    confirmation = self.voice.listen()
                
                if confirmation and 'yes' in confirmation.lower():
                    return subject
        
        # Text input fallback
        return input("Enter email subject: ").strip()
    
    def _get_email_body(self):
        """Get email body content from user."""
        if self.voice and hasattr(self.voice, 'speak') and hasattr(self.voice, 'listen'):
            self.voice.speak("What would you like to say in the email? Please dictate the message.")
            
            # Handle async listen method properly
            if asyncio.iscoroutinefunction(self.voice.listen):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    body = loop.run_until_complete(self.voice.listen())
                finally:
                    loop.close()
            else:
                body = self.voice.listen()
                
            if body:
                # Confirm body content
                preview = body[:50] + "..." if len(body) > 50 else body
                self.voice.speak(f"Your message starts with: {preview}. Is that correct? Say yes to confirm or no to try again.")
                
                # Handle async confirmation
                if asyncio.iscoroutinefunction(self.voice.listen):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        confirmation = loop.run_until_complete(self.voice.listen())
                    finally:
                        loop.close()
                else:
                    confirmation = self.voice.listen()
                
                if confirmation and 'yes' in confirmation.lower():
                    return body
        
        # Text input fallback
        return input("Enter email message: ").strip()
    
    def _clean_spoken_email(self, spoken_email):
        """Clean up spoken email address."""
        # Common voice-to-text corrections
        replacements = {
            ' at ': '@',
            ' dot ': '.',
            ' gmail ': 'gmail',
            ' com': '.com',
            ' org': '.org',
            ' edu': '.edu',
            ' net': '.net'
        }
        
        cleaned = spoken_email.lower()
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove extra spaces
        cleaned = ''.join(cleaned.split())
        
        return cleaned
    
    def _apply_personality_tone(self, body, tone='friendly'):
        """Apply personality tone to email body."""
        try:
            if tone == 'formal':
                if not body.startswith(('Dear', 'Hello', 'Greetings')):
                    body = "Dear recipient,\n\n" + body
                if not body.endswith(('Sincerely', 'Best regards', 'Regards')):
                    body += "\n\nBest regards"
                    
            elif tone == 'friendly':
                if not body.startswith(('Hi', 'Hey', 'Hello')):
                    body = "Hi!\n\n" + body
                if not body.endswith(('Thanks', 'Best', 'Cheers')):
                    body += "\n\nThanks!"
                    
            elif tone == 'professional':
                if not body.startswith(('Greetings', 'Hello', 'Dear')):
                    body = "Greetings,\n\n" + body
                if not body.endswith(('Kind regards', 'Best regards')):
                    body += "\n\nKind regards"
            
            return body
            
        except Exception as e:
            logger.warning(f"Error applying personality tone: {e}")
            return body
    
    def _confirm_email_send(self, to_email, subject, body):
        """Get user confirmation before opening Gmail."""
        preview = body[:100] + "..." if len(body) > 100 else body
        
        if self.voice and hasattr(self.voice, 'speak') and hasattr(self.voice, 'listen'):
            # Voice confirmation
            self.voice.speak(f"I'm about to open Gmail and compose an email to {to_email} with subject '{subject}'. The message is: {preview}. Should I proceed? Say yes or no.")
            
            # Handle async listen method properly
            if asyncio.iscoroutinefunction(self.voice.listen):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(self.voice.listen())
                finally:
                    loop.close()
            else:
                response = self.voice.listen()
                
            return response and 'yes' in response.lower()
        else:
            # Text confirmation
            print(f"\n--- EMAIL CONFIRMATION ---")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {preview}")
            
            confirmation = input("Open Gmail and compose this email? (yes/no): ").lower().strip()
            return confirmation in ['yes', 'y']
    
    def _automate_gmail_compose(self, to_email, subject, body):
        """
        Automate Gmail composition by opening browser and filling fields.
        """
        try:
            # Method 1: Use Gmail compose URL with pre-filled data
            gmail_compose_url = self._build_gmail_compose_url(to_email, subject, body)
            
            if self.voice and hasattr(self.voice, 'speak'):
                self.voice.speak("Opening Gmail now. Please wait while I fill in the email details.")
            
            print("🌐 Opening Gmail in your default browser...")
            webbrowser.open(gmail_compose_url)
            
            # Give user time to see what happened
            time.sleep(3)
            
            if self.voice and hasattr(self.voice, 'speak'):
                self.voice.speak("Gmail is now open with your email pre-filled. You can review and send it when ready.")
            
            print("✅ Gmail opened with pre-filled email content!")
            print("📧 Please review the email and click Send when ready.")
            
            return True
            
        except Exception as e:
            logger.error(f"Gmail automation error: {e}")
            
            # Fallback: Open regular Gmail compose
            try:
                print("🔄 Trying fallback method...")
                self._fallback_gmail_open(to_email, subject, body)
                return True
            except Exception as e2:
                logger.error(f"Fallback method also failed: {e2}")
                return False
    
    def _build_gmail_compose_url(self, to_email, subject, body):
        """Build Gmail compose URL with pre-filled data."""
        base_url = "https://mail.google.com/mail/?view=cm&fs=1"
        
        # URL encode the parameters
        params = []
        if to_email:
            params.append(f"to={quote(to_email)}")
        if subject:
            params.append(f"su={quote(subject)}")
        if body:
            params.append(f"body={quote(body)}")
        
        if params:
            return base_url + "&" + "&".join(params)
        else:
            return base_url
    
    def _fallback_gmail_open(self, to_email, subject, body):
        """Fallback method: Open Gmail and copy content to clipboard."""
        print("🔄 Using fallback method...")
        
        # Open regular Gmail
        webbrowser.open("https://mail.google.com")
        
        # Prepare content for easy copying
        email_content = f"""To: {to_email}
Subject: {subject}

{body}"""
        
        # Copy to clipboard
        pyperclip.copy(email_content)
        
        if self.voice and hasattr(self.voice, 'speak'):
            self.voice.speak("Gmail is now open. I've copied the email content to your clipboard. You can paste it into the compose window.")
        
        print("📋 Email content copied to clipboard!")
        print("📧 Please:")
        print("1. Click 'Compose' in Gmail")
        print("2. Paste the content using Ctrl+V")
        print("3. Adjust as needed and send")
        
        return True
    
    def quick_email_to_self(self, subject="Test from Zara", body="This is a test email from Zara Assistant!"):
        """Quick function to send email to yourself for testing."""
        return self.send_email_web(self.default_email, subject, body)

# Integration function for Zara's tools module
def send_email_web_integrated(to=None, subject=None, body=None, **kwargs):
    """
    Integration function for Zara's tools module.
    """
    try:
        # Import voice interface if available
        voice_interface = None
        try:
            from zara.voice import get_voice_interface
            voice_interface = get_voice_interface()
        except ImportError:
            pass  # Voice interface not available
        
        # Create web email automation instance
        web_email = WebEmailAutomation(voice_interface)
        
        # Send email
        result = web_email.send_email_web(to, subject, body, **kwargs)
        
        return result
        
    except Exception as e:
        logger.error(f"Web email integration error: {e}")
        return f"Error in web email integration: {str(e)}"

# Voice command handlers
def handle_send_email_command(voice_interface=None):
    """Handle 'send email' voice command."""
    web_email = WebEmailAutomation(voice_interface)
    return web_email.send_email_web()

def handle_email_someone_command(recipient=None, voice_interface=None):
    """Handle 'email someone' voice command."""
    web_email = WebEmailAutomation(voice_interface)
    return web_email.send_email_web(to_email=recipient) 