from typing import Optional, Any, Dict

class DatabaseError(Exception):
    """Base exception class for all database-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message

class DatabaseConnectionError(DatabaseError):
    """Exception raised for database connection issues."""
    
    def __init__(self, message: str, connection_params: Optional[Dict[str, Any]] = None):
        details = {'connection_params': {k: '***' if k in ('password', 'pwd') else v 
                                      for k, v in (connection_params or {}).items()}}
        super().__init__(f"Connection Error: {message}", details)

class DatabaseOperationError(DatabaseError):
    """Exception raised for database operation failures."""
    
    def __init__(self, message: str, query: Optional[str] = None, params: Optional[tuple] = None):
        details = {}
        if query:
            details['query'] = query
        if params:
            details['parameters'] = params
        super().__init__(f"Operation Error: {message}", details)

class ValidationError(DatabaseError):
    """Exception raised for parameter validation failures."""
    
    def __init__(self, message: str, invalid_params: Optional[Dict[str, Any]] = None):
        details = {'invalid_parameters': invalid_params} if invalid_params else {}
        super().__init__(f"Validation Error: {message}", details)

class TransactionError(DatabaseError):
    """Exception raised for transaction-related issues."""
    
    def __init__(self, message: str, transaction_state: Optional[str] = None):
        details = {'transaction_state': transaction_state} if transaction_state else {}
        super().__init__(f"Transaction Error: {message}", details)

class DataFrameOperationError(DatabaseError):
    """Exception raised for DataFrame operation failures."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {'operation': operation} if operation else {}
        super().__init__(f"DataFrame Operation Error: {message}", details)

class CredentialError(DatabaseError):
    """Exception raised for credential-related issues."""
    
    def __init__(self, message: str, username: Optional[str] = None):
        details = {'username': username} if username else {}
        super().__init__(f"Credential Error: {message}", details)

class ConfigurationError(DatabaseError):
    """Exception raised for configuration-related issues."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {'configuration_key': config_key} if config_key else {}
        super().__init__(f"Configuration Error: {message}", details)

class TemplateError(DatabaseError):
    """Exception raised for template-related issues."""
    
    def __init__(self, message: str, template_name: Optional[str] = None):
        details = {'template': template_name} if template_name else {}
        super().__init__(f"Template Error: {message}", details)

class QueryError(DatabaseError):
    """Exception raised for SQL query-related issues."""
    
    def __init__(
        self, 
        message: str, 
        query: Optional[str] = None, 
        params: Optional[tuple] = None,
        error_position: Optional[int] = None
    ):
        details = {}
        if query:
            details['query'] = query
        if params:
            details['parameters'] = params
        if error_position is not None:
            details['error_position'] = error_position
        super().__init__(f"Query Error: {message}", details)

class ExportError(DatabaseError):
    """Exception raised for data export failures."""
    
    def __init__(
        self, 
        message: str, 
        format: Optional[str] = None,
        file_path: Optional[str] = None
    ):
        details = {}
        if format:
            details['format'] = format
        if file_path:
            details['file_path'] = file_path
        super().__init__(f"Export Error: {message}", details)
