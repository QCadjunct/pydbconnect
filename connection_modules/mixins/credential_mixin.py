''' pydatabaseconnection/connection_modules/mixins/credential_mixin.py '''

from typing import Any, Dict, Optional
from ...exceptions import CredentialsError
from ...utils.decorators import log_operation

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

# pydatabaseconnection/connection_modules/mixins/parameter_mixin.py
from typing import Any, Dict, Optional
from ...exceptions import ValidationError
from ...utils.decorators import log_operation

class ParameterMixin:
    """Mixin for handling database parameters."""

    @log_operation
    def set_parameter(self: 'DatabaseConnection', key: str, value: Any) -> 'DatabaseConnection':
        """Set a single parameter."""
        if not hasattr(self, '_parameters'):
            self._parameters = {}
        self._parameters[key] = value
        return self

    @log_operation
    def set_parameters(self: 'DatabaseConnection', params: Dict[str, Any]) -> 'DatabaseConnection':
        """Set multiple parameters."""
        if not hasattr(self, '_parameters'):
            self._parameters = {}
        self._parameters.update(params)
        return self

    def get_parameter(self: 'DatabaseConnection', key: str, default: Any = None) -> Any:
        """Get parameter value."""
        return getattr(self, '_parameters', {}).get(key, default)
