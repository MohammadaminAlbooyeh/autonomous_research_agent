"""
SQLAlchemy custom types for encrypted database columns.

Provides TypeDecorator classes that automatically encrypt/decrypt
on save/load operations.
"""

from sqlalchemy import TypeDecorator, Text
from backend.encryption import get_encryption


class EncryptedString(TypeDecorator):
    """SQLAlchemy type for automatically encrypted string columns."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt value when writing to database."""
        if value is None:
            return None
        return get_encryption().encrypt(str(value))

    def process_result_value(self, value, dialect):
        """Decrypt value when reading from database."""
        if value is None:
            return None
        return get_encryption().decrypt(str(value))


class EncryptedJSON(TypeDecorator):
    """SQLAlchemy type for automatically encrypted JSON columns."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt value when writing to database."""
        if value is None:
            return None
        import json
        json_str = json.dumps(value) if not isinstance(value, str) else value
        return get_encryption().encrypt(json_str)

    def process_result_value(self, value, dialect):
        """Decrypt and parse JSON when reading from database."""
        if value is None:
            return None
        import json
        decrypted = get_encryption().decrypt(str(value))
        return json.loads(decrypted)
