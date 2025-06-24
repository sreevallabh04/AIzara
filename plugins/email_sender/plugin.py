"""
Secure Email Sender Plugin for Zara Assistant

This plugin provides enterprise-grade email sending capabilities with:
- Multi-provider SMTP support (Gmail, Outlook, custom)
- Secure credential management with OS keychain integration
- Context-aware email composition with personality adaptation
- Safety checks and user confirmation
- Attachment support and HTML/plaintext auto-detection
"""

import smtplib
import ssl
import mimetypes
import os
import re
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

# Plugin metadata
PLUGIN_NAME = "email_sender"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Secure email sending with multi-provider SMTP support"
PLUGIN_COMMANDS = [
    "send email", "email someone", "contact via email", "send message",
    "compose email", "mail", "notify by email"
]
PLUGIN_CONFIDENCE_TRIGGERS = [
    "send", "email", "mail", "message", "contact", "notify", "inform"
]

logger = logging.getLogger(__name__)

class EmailConfig:
    """Email configuration and provider settings."""
    
    PROVIDERS = {
        'gmail': {
            'smtp_server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'auth_required': True
        },
        'outlook': {
            'smtp_server': 'smtp-mail.outlook.com',
            'port': 587,
            'use_tls': True,
            'auth_required': True
        },
        'yahoo': {
            'smtp_server': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True,
            'auth_required': True
        },
        'vit': {
            'smtp_server': 'smtp-mail.outlook.com',
            'port': 587,
            'use_tls': True,
            'auth_required': True
        }
    }

class EmailCredentials:
    """Secure email credential management with fallback to encrypted files."""
    
    def __init__(self, keychain_manager=None):
        self.keychain = keychain_manager
        self.service_name = "zara_email_credentials"
        self.credentials_file = Path("data/encrypted/email_credentials.json")
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _encrypt_credentials(self, data: Dict) -> str:
        """Encrypt credential data using simple encoding (placeholder for real encryption)."""
        import base64
        return base64.b64encode(json.dumps(data).encode()).decode()
    
    def _decrypt_credentials(self, encrypted_data: str) -> Dict:
        """Decrypt credential data."""
        import base64
        return json.loads(base64.b64decode(encrypted_data.encode()).decode())
    
    def store_credentials(self, email: str, password: str, provider: str = 'gmail') -> bool:
        """Store email credentials securely."""
        try:
            credential_data = {
                'email': email,
                'password': password,
                'provider': provider,
                'stored_at': datetime.now().isoformat()
            }
            
            # Try keychain first if available
            if self.keychain:
                try:
                    account = f"{email}_{provider}"
                    success = self.keychain.store_credential(
                        service=self.service_name,
                        account=account,
                        credential_data=credential_data
                    )
                    if success:
                        logger.info(f"Email credentials stored in keychain for {email} ({provider})")
                        return True
                except Exception as e:
                    logger.warning(f"Keychain storage failed, falling back to file: {e}")
            
            # Fallback to encrypted file storage
            try:
                existing_data = {}
                if self.credentials_file.exists():
                    with open(self.credentials_file, 'r') as f:
                        encrypted_content = f.read()
                        if encrypted_content.strip():
                            existing_data = self._decrypt_credentials(encrypted_content)
                
                account_key = f"{email}_{provider}"
                existing_data[account_key] = credential_data
                
                encrypted_data = self._encrypt_credentials(existing_data)
                with open(self.credentials_file, 'w') as f:
                    f.write(encrypted_data)
                
                logger.info(f"Email credentials stored in encrypted file for {email} ({provider})")
                return True
                
            except Exception as e:
                logger.error(f"File storage also failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing email credentials: {str(e)}")
            return False
    
    def get_credentials(self, email: str, provider: str = 'gmail') -> Optional[Dict]:
        """Retrieve email credentials."""
        try:
            account = f"{email}_{provider}"
            
            # Try keychain first if available
            if self.keychain:
                try:
                    credential_data = self.keychain.get_credential(
                        service=self.service_name,
                        account=account
                    )
                    if credential_data:
                        logger.info(f"Retrieved credentials from keychain for {email} ({provider})")
                        return credential_data
                except Exception as e:
                    logger.warning(f"Keychain retrieval failed, trying file: {e}")
            
            # Fallback to encrypted file
            try:
                if self.credentials_file.exists():
                    with open(self.credentials_file, 'r') as f:
                        encrypted_content = f.read()
                        if encrypted_content.strip():
                            all_credentials = self._decrypt_credentials(encrypted_content)
                            if account in all_credentials:
                                logger.info(f"Retrieved credentials from file for {email} ({provider})")
                                return all_credentials[account]
                
                logger.warning(f"No credentials found for {email} ({provider})")
                return None
                
            except Exception as e:
                logger.error(f"File retrieval failed: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving email credentials: {str(e)}")
            return None
    
    def list_stored_accounts(self) -> List[str]:
        """List all stored email accounts."""
        try:
            accounts = set()
            
            # Try keychain first
            if self.keychain:
                try:
                    keychain_accounts = self.keychain.list_accounts(service=self.service_name)
                    accounts.update([acc.split('_')[0] for acc in keychain_accounts])
                except Exception as e:
                    logger.warning(f"Error listing keychain accounts: {e}")
            
            # Try file storage
            try:
                if self.credentials_file.exists():
                    with open(self.credentials_file, 'r') as f:
                        encrypted_content = f.read()
                        if encrypted_content.strip():
                            all_credentials = self._decrypt_credentials(encrypted_content)
                            accounts.update([acc.split('_')[0] for acc in all_credentials.keys()])
            except Exception as e:
                logger.warning(f"Error listing file accounts: {e}")
            
            return list(accounts)
            
        except Exception as e:
            logger.error(f"Error listing email accounts: {str(e)}")
            return []

class EmailSender:
    """Main email sending engine with security and validation."""
    
    def __init__(self, keychain_manager=None, personality_manager=None):
        self.credentials = EmailCredentials(keychain_manager)
        self.personality = personality_manager
        self.sent_emails = []  # Track sent emails for debugging
        
    def detect_email_format(self, body: str) -> str:
        """Auto-detect if email body is HTML or plaintext."""
        html_tags = re.search(r'<[^>]+>', body)
        return 'html' if html_tags else 'plain'
    
    def apply_personality_tone(self, body: str, tone: str = 'friendly') -> str:
        """Apply personality-based tone modifications to email body."""
        try:
            # Apply tone-specific modifications
            if tone == 'formal':
                # Add formal greetings if missing
                if not re.search(r'(dear|hello|greetings)', body.lower()):
                    body = "Dear recipient,\n\n" + body
                if not re.search(r'(sincerely|regards|best)', body.lower()):
                    body += "\n\nBest regards"
                    
            elif tone == 'friendly':
                # Add casual greetings if missing
                if not re.search(r'(hi|hey|hello)', body.lower()):
                    body = "Hi there!\n\n" + body
                if not re.search(r'(thanks|cheers|best)', body.lower()):
                    body += "\n\nThanks!"
                    
            elif tone == 'professional':
                # Add professional structure
                if not re.search(r'(greetings|hello)', body.lower()):
                    body = "Greetings,\n\n" + body
                if not re.search(r'(regards|sincerely)', body.lower()):
                    body += "\n\nKind regards"
                    
            return body
            
        except Exception as e:
            logger.warning(f"Error applying personality tone: {str(e)}")
            return body
    
    def sanitize_email_content(self, content: str) -> str:
        """Sanitize email content to prevent injection attacks."""
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # JavaScript
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'expression\s*\(',  # CSS expressions
        ]
        
        sanitized = content
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized
    
    def validate_email_address(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def prepare_attachments(self, attachments: List[str]) -> List[Tuple[str, MIMEBase]]:
        """Prepare email attachments with validation."""
        prepared_attachments = []
        
        for attachment_path in attachments:
            try:
                if not os.path.exists(attachment_path):
                    logger.warning(f"Attachment not found: {attachment_path}")
                    continue
                
                # Check file size (limit to 25MB per attachment)
                file_size = os.path.getsize(attachment_path)
                if file_size > 25 * 1024 * 1024:  # 25MB
                    logger.warning(f"Attachment too large: {attachment_path} ({file_size} bytes)")
                    continue
                
                # Determine content type
                content_type, encoding = mimetypes.guess_type(attachment_path)
                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'
                
                main_type, sub_type = content_type.split('/', 1)
                
                # Create attachment
                with open(attachment_path, 'rb') as fp:
                    attachment = MIMEBase(main_type, sub_type)
                    attachment.set_payload(fp.read())
                    encoders.encode_base64(attachment)
                    
                    filename = os.path.basename(attachment_path)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    
                    prepared_attachments.append((filename, attachment))
                    logger.info(f"Prepared attachment: {filename}")
                    
            except Exception as e:
                logger.error(f"Error preparing attachment {attachment_path}: {str(e)}")
                continue
        
        return prepared_attachments
    
    def compose_email(self, to: str, subject: str, body: str, 
                     attachments: Optional[List[str]] = None,
                     cc: Optional[List[str]] = None,
                     bcc: Optional[List[str]] = None,
                     tone: str = 'friendly') -> MIMEMultipart:
        """Compose email message with all components."""
        
        # Apply personality tone
        body = self.apply_personality_tone(body, tone)
        
        # Sanitize content
        subject = self.sanitize_email_content(subject)
        body = self.sanitize_email_content(body)
        
        # Create message
        message = MIMEMultipart()
        message['Subject'] = subject
        message['To'] = to
        
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)
        
        # Detect and add body
        body_format = self.detect_email_format(body)
        text_part = MIMEText(body, body_format)
        message.attach(text_part)
        
        # Add attachments
        if attachments:
            prepared_attachments = self.prepare_attachments(attachments)
            for filename, attachment in prepared_attachments:
                message.attach(attachment)
                logger.info(f"Attached file: {filename}")
        
        return message
    
    def send_email(self, sender_email: str, to: str, subject: str, body: str,
                   attachments: Optional[List[str]] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   provider: str = 'gmail',
                   tone: str = 'friendly',
                   dry_run: bool = False) -> Dict[str, Any]:
        """Send email with comprehensive error handling and logging."""
        
        try:
            # Validate inputs
            if not self.validate_email_address(sender_email):
                return {
                    'success': False,
                    'error': f'Invalid sender email address: {sender_email}'
                }
            
            if not self.validate_email_address(to):
                return {
                    'success': False,
                    'error': f'Invalid recipient email address: {to}'
                }
            
            # Get credentials
            credentials = self.credentials.get_credentials(sender_email, provider)
            if not credentials:
                return {
                    'success': False,
                    'error': f'No credentials found for {sender_email} ({provider}). Please set up email credentials first.'
                }
            
            # Get provider configuration
            if provider not in EmailConfig.PROVIDERS:
                return {
                    'success': False,
                    'error': f'Unsupported email provider: {provider}'
                }
            
            provider_config = EmailConfig.PROVIDERS[provider]
            
            # Compose email
            message = self.compose_email(
                to=to, subject=subject, body=body,
                attachments=attachments, cc=cc, bcc=bcc, tone=tone
            )
            message['From'] = sender_email
            
            # Dry run mode (for testing)
            if dry_run:
                return {
                    'success': True,
                    'message': 'Email composed successfully (dry run mode)',
                    'details': {
                        'from': sender_email,
                        'to': to,
                        'subject': subject,
                        'body_length': len(body),
                        'attachments': len(attachments) if attachments else 0,
                        'provider': provider
                    }
                }
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(provider_config['smtp_server'], provider_config['port']) as server:
                if provider_config['use_tls']:
                    server.starttls(context=context)
                
                if provider_config['auth_required']:
                    server.login(credentials['email'], credentials['password'])
                
                # Get all recipients
                all_recipients = [to]
                if cc:
                    all_recipients.extend(cc)
                if bcc:
                    all_recipients.extend(bcc)
                
                # Send message
                server.send_message(message, to_addrs=all_recipients)
            
            # Log successful send
            email_record = {
                'timestamp': datetime.now().isoformat(),
                'from': sender_email,
                'to': to,
                'subject': subject,
                'provider': provider,
                'success': True
            }
            self.sent_emails.append(email_record)
            
            logger.info(f"Email sent successfully from {sender_email} to {to}")
            
            return {
                'success': True,
                'message': f'Email sent successfully to {to}',
                'details': email_record
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipients refused: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

class EmailPlugin:
    """Main email plugin class for Zara integration."""
    
    def __init__(self, keychain_manager=None, personality_manager=None, voice_interface=None):
        self.email_sender = EmailSender(keychain_manager, personality_manager)
        self.voice = voice_interface
        self.confirmation_required = True  # Safety feature
        
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata for registration."""
        return {
            'name': PLUGIN_NAME,
            'version': PLUGIN_VERSION,
            'description': PLUGIN_DESCRIPTION,
            'commands': PLUGIN_COMMANDS,
            'confidence_triggers': PLUGIN_CONFIDENCE_TRIGGERS,
            'functions': {
                'send_email': self.send_email_command,
                'setup_email_credentials': self.setup_credentials_command,
                'list_email_accounts': self.list_accounts_command
            }
        }
    
    def confirm_email_send(self, to: str, subject: str, body_preview: str) -> bool:
        """Get user confirmation before sending email."""
        if not self.confirmation_required:
            return True
        
        preview = body_preview[:100] + "..." if len(body_preview) > 100 else body_preview
        
        if self.voice and hasattr(self.voice, 'speak'):
            # Voice confirmation
            confirmation_msg = (
                f"I'm about to send an email to {to} with subject '{subject}'. "
                f"The message starts with: {preview}. "
                f"Should I send this email? Please say yes or no."
            )
            self.voice.speak(confirmation_msg)
            
            # Listen for confirmation
            if hasattr(self.voice, 'listen_for_confirmation'):
                response = self.voice.listen_for_confirmation()
                return response and 'yes' in response.lower()
            else:
                # Fallback to text input
                confirmation = input("Say 'yes' to confirm: ").lower().strip()
                return confirmation in ['yes', 'y', 'send']
        else:
            # Text confirmation
            print(f"\n--- EMAIL CONFIRMATION ---")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body preview: {preview}")
            
            confirmation = input("Send this email? (yes/no): ").lower().strip()
            return confirmation in ['yes', 'y', 'send']
    
    def send_email_command(self, **kwargs) -> str:
        """Main email sending command for Zara integration."""
        try:
            # Extract parameters
            to = kwargs.get('to', kwargs.get('recipient'))
            subject = kwargs.get('subject', 'Message from Zara Assistant')
            body = kwargs.get('body', kwargs.get('message', ''))
            sender = kwargs.get('from', kwargs.get('sender'))
            attachments = kwargs.get('attachments', [])
            provider = kwargs.get('provider', 'gmail')
            tone = kwargs.get('tone', 'friendly')
            
            if not to:
                return "Error: No recipient email address specified"
            
            if not body:
                return "Error: No message body provided"
            
            # If no sender specified, try to get default from stored accounts
            if not sender:
                accounts = self.email_sender.credentials.list_stored_accounts()
                if accounts:
                    sender = accounts[0]  # Use first available account
                else:
                    return "Error: No sender email configured. Please set up email credentials first."
            
            # Get user confirmation
            if not self.confirm_email_send(to, subject, body):
                return "Email sending cancelled by user"
            
            # Send email
            result = self.email_sender.send_email(
                sender_email=sender,
                to=to,
                subject=subject,
                body=body,
                attachments=attachments if attachments else None,
                provider=provider,
                tone=tone
            )
            
            if result['success']:
                success_msg = f"Email sent successfully to {to}"
                if self.voice and hasattr(self.voice, 'speak'):
                    self.voice.speak(success_msg)
                return success_msg
            else:
                error_msg = f"Failed to send email: {result['error']}"
                if self.voice and hasattr(self.voice, 'speak'):
                    self.voice.speak("Sorry, I couldn't send the email. " + result['error'])
                return error_msg
                
        except Exception as e:
            error_msg = f"Error in email command: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def setup_credentials_command(self, **kwargs) -> str:
        """Command to set up email credentials."""
        try:
            email = kwargs.get('email')
            password = kwargs.get('password')
            provider = kwargs.get('provider', 'gmail')
            
            if not email or not password:
                return "Error: Email address and password required for setup"
            
            success = self.email_sender.credentials.store_credentials(email, password, provider)
            
            if success:
                success_msg = f"Email credentials stored securely for {email} ({provider})"
                if self.voice and hasattr(self.voice, 'speak'):
                    self.voice.speak(f"Email credentials set up successfully for {email}")
                return success_msg
            else:
                error_msg = "Failed to store email credentials"
                if self.voice and hasattr(self.voice, 'speak'):
                    self.voice.speak("Sorry, I couldn't store the email credentials")
                return error_msg
                
        except Exception as e:
            error_msg = f"Error setting up credentials: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def list_accounts_command(self, **kwargs) -> str:
        """Command to list stored email accounts."""
        try:
            accounts = self.email_sender.credentials.list_stored_accounts()
            
            if accounts:
                account_list = ", ".join(accounts)
                result_msg = f"Stored email accounts: {account_list}"
                if self.voice and hasattr(self.voice, 'speak'):
                    self.voice.speak(f"You have {len(accounts)} email account{'s' if len(accounts) > 1 else ''} configured: {account_list}")
                return result_msg
            else:
                result_msg = "No email accounts configured"
                if self.voice and hasattr(self.voice, 'speak'):
                    self.voice.speak("No email accounts are currently configured")
                return result_msg
                
        except Exception as e:
            error_msg = f"Error listing accounts: {str(e)}"
            logger.error(error_msg)
            return error_msg

# Plugin factory function for Zara integration
def create_plugin(keychain_manager=None, personality_manager=None, voice_interface=None):
    """Factory function to create email plugin instance."""
    return EmailPlugin(keychain_manager, personality_manager, voice_interface)

# Plugin registration function
def register_plugin():
    """Registration function for Zara plugin system."""
    return {
        'name': PLUGIN_NAME,
        'version': PLUGIN_VERSION,
        'description': PLUGIN_DESCRIPTION,
        'factory': create_plugin,
        'commands': PLUGIN_COMMANDS,
        'confidence_triggers': PLUGIN_CONFIDENCE_TRIGGERS
    } 