"""Base exceptions for database operations."""


class BaseDatabaseError(Exception):
    """Base exception for all database errors."""

    pass


class BaseConnectionError(Exception):
    """Base exception for all connection errors."""

    pass
