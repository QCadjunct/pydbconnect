# pydatabaseconnection/__init__.py
"""
PyDatabaseConnection - A fluent interface for database operations.

This package provides a template-driven approach to database connections
with integrated DataFrame operations and transaction management.
"""

from .core.connection import DatabaseConnection
from .core.template_manager import TemplateManager
from .types.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseOperationError,
    ValidationError,
    DataFrameOperationError
)
from .types.connection_types import (
    ConnectionConfig,
    Credentials,
    ConnectionMode
)

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    'DatabaseConnection',
    'TemplateManager',
    'DatabaseError',
    'DatabaseConnectionError',
    'DatabaseOperationError',
    'ValidationError',
    'DataFrameOperationError',
    'ConnectionConfig',
    'Credentials',
    'ConnectionMode'
]
