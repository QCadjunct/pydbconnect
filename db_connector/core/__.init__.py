"""Database connector core package."""

from .connector import (
    DatabaseConnector,
    DatabaseError,
    ConnectionError,
    CredentialsError,
)
from .multi_connector import MultiDatabaseConnector
