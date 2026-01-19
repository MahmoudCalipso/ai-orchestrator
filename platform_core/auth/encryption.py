"""
Encryption Service for sensitive data (Tokens, Credentials)
"""
import os
import base64
from cryptography.fernet import Fernet
from typing import Optional

class EncryptionService:
    def __init__(self):
        # Use MASTER_ENCRYPTION_KEY or fallback to JWT_SECRET_KEY
        key = os.getenv("MASTER_ENCRYPTION_KEY") or os.getenv("JWT_SECRET_KEY")
        if not key:
            raise ValueError("MASTER_ENCRYPTION_KEY or JWT_SECRET_KEY must be set")
            
        # Fernet requires a 32-byte url-safe base64 key
        # We derive it from the secret key to ensure consistency
        derived_key = base64.urlsafe_b64encode(key.encode().ljust(32)[:32])
        self.cipher = Fernet(derived_key)

    def encrypt(self, data: str) -> str:
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # Fallback if decryption fails (e.g. if key changed or data was already plain)
            return encrypted_data

encryption_service = EncryptionService()
