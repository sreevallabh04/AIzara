"""
Secure Keychain Manager for Zara Assistant

Cross-platform credential management with OS keychain integration and
encrypted file fallback for secure storage of sensitive data.

Supports:
- Windows Credential Manager
- macOS Keychain
- Linux Secret Service API
- Encrypted file fallback for all platforms
"""

import os
import sys
import json
import base64
import platform
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class KeychainManager:
    """
    Cross-platform keychain manager with secure credential storage.
    
    This class provides a unified interface for storing and retrieving
    credentials across different operating systems, with automatic
    fallback to encrypted file storage when OS keychain is unavailable.
    """
    
    def __init__(self, use_os_keychain: bool = True, encryption_key: Optional[str] = None):
        """
        Initialize the keychain manager.
        
        Args:
            use_os_keychain: Whether to attempt OS keychain integration
            encryption_key: Optional encryption key for file storage
        """
        self.use_os_keychain = use_os_keychain
        self.platform = platform.system().lower()
        self.encryption_key = encryption_key
        self.credentials_dir = Path("data/encrypted")
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.credentials_dir / "keychain.json"
        
        # Initialize OS-specific keychain
        self._keychain_available = False
        if self.use_os_keychain:
            self._init_os_keychain()
    
    def _init_os_keychain(self):
        """Initialize OS-specific keychain support."""
        try:
            if self.platform == "windows":
                self._init_windows_keychain()
            elif self.platform == "darwin":  # macOS
                self._init_macos_keychain()
            elif self.platform == "linux":
                self._init_linux_keychain()
            else:
                logger.warning(f"Unsupported platform for OS keychain: {self.platform}")
        except Exception as e:
            logger.warning(f"Failed to initialize OS keychain: {e}")
    
    def _init_windows_keychain(self):
        """Initialize Windows Credential Manager support."""
        try:
            import win32cred
            import win32api
            self._win32cred = win32cred
            self._win32api = win32api
            self._keychain_available = True
            logger.info("Windows Credential Manager initialized")
        except ImportError:
            logger.warning("pywin32 not available, falling back to file storage")
        except Exception as e:
            logger.warning(f"Windows credential manager initialization failed: {e}")
    
    def _init_macos_keychain(self):
        """Initialize macOS Keychain support."""
        try:
            import keyring
            self._keyring = keyring
            self._keychain_available = True
            logger.info("macOS Keychain initialized")
        except ImportError:
            logger.warning("keyring library not available, falling back to file storage")
        except Exception as e:
            logger.warning(f"macOS keychain initialization failed: {e}")
    
    def _init_linux_keychain(self):
        """Initialize Linux Secret Service support."""
        try:
            import keyring
            self._keyring = keyring
            self._keychain_available = True
            logger.info("Linux Secret Service initialized")
        except ImportError:
            logger.warning("keyring library not available, falling back to file storage")
        except Exception as e:
            logger.warning(f"Linux secret service initialization failed: {e}")
    
    def _generate_encryption_key(self) -> str:
        """Generate a simple encryption key for file storage."""
        if self.encryption_key:
            return self.encryption_key
        
        # Use machine-specific information to generate a consistent key
        import hashlib
        machine_info = f"{platform.node()}{platform.processor()}{platform.system()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:32]
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using simple XOR cipher with base64 encoding."""
        key = self._generate_encryption_key()
        encrypted = []
        
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            encrypted.append(chr(ord(char) ^ ord(key_char)))
        
        encrypted_str = ''.join(encrypted)
        return base64.b64encode(encrypted_str.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using simple XOR cipher with base64 decoding."""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode()).decode()
            key = self._generate_encryption_key()
            decrypted = []
            
            for i, char in enumerate(decoded_data):
                key_char = key[i % len(key)]
                decrypted.append(chr(ord(char) ^ ord(key_char)))
            
            return ''.join(decrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return ""
    
    def _store_os_credential(self, service: str, account: str, credential_data: Dict) -> bool:
        """Store credential in OS keychain."""
        try:
            credential_json = json.dumps(credential_data)
            
            if self.platform == "windows" and hasattr(self, '_win32cred'):
                # Windows Credential Manager
                self._win32cred.CredWrite({
                    'Type': self._win32cred.CRED_TYPE_GENERIC,
                    'TargetName': f"{service}:{account}",
                    'UserName': account,
                    'CredentialBlob': credential_json,
                    'Comment': 'Zara Assistant credential',
                    'Persist': self._win32cred.CRED_PERSIST_LOCAL_MACHINE
                })
                return True
                
            elif self.platform in ["darwin", "linux"] and hasattr(self, '_keyring'):
                # macOS/Linux keyring
                self._keyring.set_password(service, account, credential_json)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to store OS credential: {e}")
            return False
    
    def _get_os_credential(self, service: str, account: str) -> Optional[Dict]:
        """Retrieve credential from OS keychain."""
        try:
            if self.platform == "windows" and hasattr(self, '_win32cred'):
                # Windows Credential Manager
                target_name = f"{service}:{account}"
                cred = self._win32cred.CredRead(target_name, self._win32cred.CRED_TYPE_GENERIC)
                if cred:
                    credential_json = cred['CredentialBlob'].decode('utf-8')
                    return json.loads(credential_json)
                    
            elif self.platform in ["darwin", "linux"] and hasattr(self, '_keyring'):
                # macOS/Linux keyring
                credential_json = self._keyring.get_password(service, account)
                if credential_json:
                    return json.loads(credential_json)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve OS credential: {e}")
            return None
    
    def _delete_os_credential(self, service: str, account: str) -> bool:
        """Delete credential from OS keychain."""
        try:
            if self.platform == "windows" and hasattr(self, '_win32cred'):
                # Windows Credential Manager
                target_name = f"{service}:{account}"
                self._win32cred.CredDelete(target_name, self._win32cred.CRED_TYPE_GENERIC)
                return True
                
            elif self.platform in ["darwin", "linux"] and hasattr(self, '_keyring'):
                # macOS/Linux keyring
                self._keyring.delete_password(service, account)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete OS credential: {e}")
            return False
    
    def _list_os_credentials(self, service: str) -> List[str]:
        """List accounts for a service in OS keychain."""
        try:
            accounts = []
            
            if self.platform == "windows" and hasattr(self, '_win32cred'):
                # Windows Credential Manager - enumerate credentials
                try:
                    creds = self._win32cred.CredEnumerate()
                    for cred in creds:
                        target_name = cred['TargetName']
                        if target_name.startswith(f"{service}:"):
                            account = target_name.split(':', 1)[1]
                            accounts.append(account)
                except:
                    pass  # No credentials or access error
                    
            # Note: keyring library doesn't provide enumeration functionality
            # for macOS/Linux, so we can't list credentials
            
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to list OS credentials: {e}")
            return []
    
    def _store_file_credential(self, service: str, account: str, credential_data: Dict) -> bool:
        """Store credential in encrypted file."""
        try:
            # Load existing credentials
            all_credentials = {}
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    encrypted_content = f.read()
                    if encrypted_content.strip():
                        decrypted_content = self._decrypt_data(encrypted_content)
                        if decrypted_content:
                            all_credentials = json.loads(decrypted_content)
            
            # Add new credential
            service_key = service
            if service_key not in all_credentials:
                all_credentials[service_key] = {}
            
            all_credentials[service_key][account] = {
                **credential_data,
                'stored_at': datetime.now().isoformat(),
                'storage_type': 'file'
            }
            
            # Encrypt and save
            credentials_json = json.dumps(all_credentials, indent=2)
            encrypted_data = self._encrypt_data(credentials_json)
            
            with open(self.credentials_file, 'w') as f:
                f.write(encrypted_data)
            
            logger.info(f"Credential stored in file for {service}:{account}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store file credential: {e}")
            return False
    
    def _get_file_credential(self, service: str, account: str) -> Optional[Dict]:
        """Retrieve credential from encrypted file."""
        try:
            if not self.credentials_file.exists():
                return None
            
            with open(self.credentials_file, 'r') as f:
                encrypted_content = f.read()
                if not encrypted_content.strip():
                    return None
                
                decrypted_content = self._decrypt_data(encrypted_content)
                if not decrypted_content:
                    return None
                
                all_credentials = json.loads(decrypted_content)
                
                if service in all_credentials and account in all_credentials[service]:
                    return all_credentials[service][account]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve file credential: {e}")
            return None
    
    def _list_file_credentials(self, service: str) -> List[str]:
        """List accounts for a service in encrypted file."""
        try:
            if not self.credentials_file.exists():
                return []
            
            with open(self.credentials_file, 'r') as f:
                encrypted_content = f.read()
                if not encrypted_content.strip():
                    return []
                
                decrypted_content = self._decrypt_data(encrypted_content)
                if not decrypted_content:
                    return []
                
                all_credentials = json.loads(decrypted_content)
                
                if service in all_credentials:
                    return list(all_credentials[service].keys())
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to list file credentials: {e}")
            return []
    
    def store_credential(self, service: str, account: str, credential_data: Dict) -> bool:
        """
        Store a credential securely.
        
        Args:
            service: Service name (e.g., 'zara_email_credentials')
            account: Account identifier (e.g., 'user@example.com_gmail')
            credential_data: Dictionary containing credential information
            
        Returns:
            bool: True if stored successfully
        """
        try:
            # Try OS keychain first if available
            if self._keychain_available:
                if self._store_os_credential(service, account, credential_data):
                    logger.info(f"Credential stored in OS keychain for {service}:{account}")
                    return True
                else:
                    logger.warning(f"OS keychain storage failed, falling back to file for {service}:{account}")
            
            # Fallback to encrypted file storage
            return self._store_file_credential(service, account, credential_data)
            
        except Exception as e:
            logger.error(f"Failed to store credential: {e}")
            return False
    
    def get_credential(self, service: str, account: str) -> Optional[Dict]:
        """
        Retrieve a credential.
        
        Args:
            service: Service name
            account: Account identifier
            
        Returns:
            Dict or None: Credential data if found
        """
        try:
            # Try OS keychain first if available
            if self._keychain_available:
                credential_data = self._get_os_credential(service, account)
                if credential_data:
                    logger.info(f"Credential retrieved from OS keychain for {service}:{account}")
                    return credential_data
            
            # Try encrypted file storage
            credential_data = self._get_file_credential(service, account)
            if credential_data:
                logger.info(f"Credential retrieved from file for {service}:{account}")
                return credential_data
            
            logger.warning(f"No credential found for {service}:{account}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve credential: {e}")
            return None
    
    def delete_credential(self, service: str, account: str) -> bool:
        """
        Delete a credential.
        
        Args:
            service: Service name
            account: Account identifier
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            success = False
            
            # Try to delete from OS keychain
            if self._keychain_available:
                if self._delete_os_credential(service, account):
                    logger.info(f"Credential deleted from OS keychain for {service}:{account}")
                    success = True
            
            # Also try to delete from file storage
            try:
                if self.credentials_file.exists():
                    with open(self.credentials_file, 'r') as f:
                        encrypted_content = f.read()
                        if encrypted_content.strip():
                            decrypted_content = self._decrypt_data(encrypted_content)
                            if decrypted_content:
                                all_credentials = json.loads(decrypted_content)
                                
                                if service in all_credentials and account in all_credentials[service]:
                                    del all_credentials[service][account]
                                    
                                    # Remove service if empty
                                    if not all_credentials[service]:
                                        del all_credentials[service]
                                    
                                    # Save updated credentials
                                    credentials_json = json.dumps(all_credentials, indent=2)
                                    encrypted_data = self._encrypt_data(credentials_json)
                                    
                                    with open(self.credentials_file, 'w') as f:
                                        f.write(encrypted_data)
                                    
                                    logger.info(f"Credential deleted from file for {service}:{account}")
                                    success = True
            except Exception as e:
                logger.warning(f"Failed to delete from file storage: {e}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete credential: {e}")
            return False
    
    def list_accounts(self, service: str) -> List[str]:
        """
        List all accounts for a service.
        
        Args:
            service: Service name
            
        Returns:
            List[str]: List of account identifiers
        """
        try:
            accounts = set()
            
            # Get accounts from OS keychain
            if self._keychain_available:
                os_accounts = self._list_os_credentials(service)
                accounts.update(os_accounts)
            
            # Get accounts from file storage
            file_accounts = self._list_file_credentials(service)
            accounts.update(file_accounts)
            
            return list(accounts)
            
        except Exception as e:
            logger.error(f"Failed to list accounts: {e}")
            return []
    
    def get_keychain_info(self) -> Dict[str, Any]:
        """
        Get information about the keychain manager.
        
        Returns:
            Dict: Information about keychain capabilities and status
        """
        return {
            'platform': self.platform,
            'os_keychain_available': self._keychain_available,
            'file_storage_available': True,
            'credentials_file': str(self.credentials_file),
            'credentials_file_exists': self.credentials_file.exists(),
            'use_os_keychain': self.use_os_keychain
        } 