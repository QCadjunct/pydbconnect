# pydatabaseconnection/exceptions/database_exceptions.py
"""Database exceptions module."""
class DatabaseError(Exception):
    """Base exception for all database related errors."""
    pass

class ConnectionError(DatabaseError):
    """Connection related errors."""
    pass

class ExecutionError(DatabaseError):
    """Query execution related errors."""
    pass

class ValidationError(DatabaseError):
    """Data validation related errors."""
    pass

class CredentialsError(DatabaseError):
    """Credential related errors."""
    pass