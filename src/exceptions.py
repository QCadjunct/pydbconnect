# exceptions.py
"""
Exception hierarchy for database operations.

This module defines the exception classes for the database connection library.
Follows a simple hierarchy where DatabaseError is the base exception,
and specific exception types inherit from it.
"""

class DatabaseError(Exception):
    """
    Base exception for all database-related errors.
    
    All other exceptions in this module inherit from this class to allow
    for generic error catching while still maintaining error specificity.
    """
    pass

class ConnectionError(DatabaseError):
    """
    Raised when database connection fails.
    
    Examples:
        - Server unavailable
        - Network issues
        - Invalid connection parameters
    """
    pass

class CredentialsError(DatabaseError):
    """
    Raised for authentication and credential issues.
    
    Examples:
        - Invalid username/password
        - Missing required credentials
        - Expired credentials
    """
    pass
class ValidationError(DatabaseError):
    """Exception raised for data validation failures."""
    
    def __init__(self, field: str, message: str, value: any = None):
        self.field = field
        self.value = value
        super().__init__(f"{field}: {message}")

class QueryError(DatabaseError):
    """
    Raised when query execution fails.
    
    Examples:
        - Syntax errors
        - Invalid table/column references
        - Constraint violations
    """
    pass

class ParameterError(DatabaseError):
    """
    Raised for invalid parameter configurations.
    
    Examples:
        - Missing required parameters
        - Invalid parameter types
        - Parameter value out of range
    """
    pass

class TransactionError(DatabaseError):
    """
    Raised for transaction-related failures.
    
    Examples:
        - Failed commits
        - Rollback errors
        - Deadlocks
    """
    pass

class ConfigurationError(DatabaseError):
    """
    Raised for configuration-related issues.
    
    Examples:
        - Missing configuration files
        - Invalid configuration format
        - Unsupported database engine
    """
    pass


class DSNUnsupportedByTragetEngineError(Exception):
    """ Raised when DSN is not supported by target engine """
    pass


# Error code mapping for standard database errors
ERROR_CODES = {
    # Connection errors
    "CONNECTION_FAILED": ("E001", "Failed to establish database connection"),
    "CONNECTION_TIMEOUT": ("E002", "Connection attempt timed out"),
    "CONNECTION_CLOSED": ("E003", "Connection unexpectedly closed"),
    
    # Authentication errors
    "INVALID_CREDENTIALS": ("A001", "Invalid username or password"),
    "MISSING_CREDENTIALS": ("A002", "Required credentials not provided"),
    
    # Query errors
    "QUERY_SYNTAX": ("Q001", "SQL syntax error"),
    "QUERY_TIMEOUT": ("Q002", "Query execution timed out"),
    
    # Transaction errors
    "TRANSACTION_FAILED": ("T001", "Transaction failed to complete"),
    "DEADLOCK": ("T002", "Deadlock detected"),
    
    # Configuration errors
    "INVALID_CONFIG": ("C001", "Invalid configuration"),
    "MISSING_CONFIG": ("C002", "Required configuration missing")
}

def get_error_info(code: str) -> tuple:
    """
    Get error code and message for a given error type.
    
    Args:
        code: The error code key string
        
    Returns:
        tuple: (error_code, error_message)
        
    Example:
        code, message = get_error_info("CONNECTION_FAILED")
    """
    return ERROR_CODES.get(code, ("UNKNOWN", "Unknown error occurred"))

def create_error(error_type: type, code: str, detail: str = "") -> Exception:
    """
    Create an exception with detailed error information.
    
    Args:
        error_type: The exception class to create
        code: The error code key string
        detail: Additional error details
        
    Returns:
        Exception: Configured exception instance
        
    Example:
        raise create_error(ConnectionError, "CONNECTION_FAILED", "Host unreachable")
    """
    error_code, error_message = get_error_info(code)
    message = f"[{error_code}] {error_message}"
    if detail:
        message += f": {detail}"
    return error_type(message)

"""
This simplified approach:

1. Moves all engine-specific logic to templates
2. Keeps enums as simple value containers
3. Provides essential exception types
4. Removes redundant validation logic
5. Makes the system more maintainable

The key changes:
- Removed hardcoded engine checks
- Simplified enum properties to basic lookups
- Added ValidationError exception
- Kept only essential exception types
- Removed redundant validation methods

Each engine's capabilities and requirements are now determined by its template, 
following the principle of "a thing should be as simple as it can be, but not simpler."

Would you like me to show how this integrates with the other modules, 
particularly how the templates would work with this simplified structure?
"""