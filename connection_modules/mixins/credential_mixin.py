# pydatabaseconnection/connection_modules/mixins/credential_mixin.py
from typing import Any, Dict, Optional
from ...exceptions import CredentialsError
from ...utility.decorators import log_operation

class CredentialMixin:
    """Mixin for handling database credentials."""
    
    @log_operation
    def set_credentials(self: 'DatabaseConnection', username: str, password: str) -> 'DatabaseConnection':
        """Set database credentials."""
        self._username = username
        self._password = password
        return self

    @log_operation
    def clear_credentials(self: 'DatabaseConnection') -> 'DatabaseConnection':
        """Clear stored credentials."""
        self._username = None
        self._password = None
        return self

    @property
    def has_credentials(self: 'DatabaseConnection') -> bool:
        """Check if credentials are set."""
        return bool(getattr(self, '_username', None) and getattr(self, '_password', None))
