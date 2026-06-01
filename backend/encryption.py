"""
Database encryption module for securing sensitive data at rest.

Provides encryption/decryption utilities for sensitive fields like API keys,
user credentials, and personal information.
"""

from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseEncryption:
    """Handle encryption and decryption of sensitive database fields."""

    def __init__(self):
        """Initialize encryption with key from environment or generate new one."""
        key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY not set in environment variables. "
                "Generate one with: from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())"
            )
        
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string (base64-encoded)
        """
        if not plaintext:
            return ""
        
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: Encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
        
        decrypted = self.cipher.decrypt(ciphertext.encode())
        return decrypted.decode()


# Global encryption instance
_encryption = None


def get_encryption() -> DatabaseEncryption:
    """Get or create global encryption instance."""
    global _encryption
    if _encryption is None:
        _encryption = DatabaseEncryption()
    return _encryption
