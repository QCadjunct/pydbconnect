"""Utility decorators."""

from typing import Dict, Any, Callable
from functools import wraps
from inspect import signature

# Import needed custom types
from templates.constraints import IsolationLevel
from templates.exceptions import DatabaseError, ConnectionError


def preload_parameters(preload_method: Callable) -> Callable:
    """
    Decorator that preloads default parameters and merges them with custom parameters.

    Args:
        preload_method: Method that returns default parameters dictionary

    Returns:
        Wrapped method with merged parameters
    """

    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, **params: Any) -> Any:
            # Validate preload method
            if not callable(preload_method):
                raise ValueError("preload_method must be callable")

            # Get default parameters
            default_params = preload_method(self)
            if not isinstance(default_params, dict):
                raise TypeError("preload_method must return a dictionary")

            # Create new params dict with defaults
            merged_params = default_params.copy()
            # Update with any passed params
            merged_params.update(params)

            # Call the method with merged parameters
            return method(self, **merged_params)

        return wrapper

    return decorator


def ensure_connected(f: Callable) -> Callable:
    """
    Decorator to ensure database connection exists before executing a method.

    Args:
        f: Method to wrap

    Returns:
        Wrapped method that checks connection status

    Raises:
        ConnectionError: If database not connected
    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_connection") or self._connection is None:
            raise ConnectionError("Database connection not established")
        return f(self, *args, **kwargs)

    return wrapper


def with_isolation_level(isolation_level: IsolationLevel):
    """Decorator for setting isolation level."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._connection:
                raise ConnectionError("No database connection")

            # Store current isolation level
            original_level = self._get_current_isolation_level()

            try:
                # Set new isolation level
                with self._cursor() as cursor:
                    cursor.execute(isolation_level.get_sql_statement())
                return func(self, *args, **kwargs)
            finally:
                # Restore original isolation level
                if original_level:
                    with self._cursor() as cursor:
                        cursor.execute(original_level.get_sql_statement())

        return wrapper

    return decorator


def transactional(nested: bool = False):
    """Decorator for transaction control."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._connection:
                raise ConnectionError("No database connection")

            if nested and not self._transaction_active:
                raise DatabaseError("No active transaction for nested operation")

            savepoint_name = None
            if nested:
                savepoint_name = f"SP_{func.__name__}_{id(func)}"
                self.create_savepoint(savepoint_name)

            try:
                result = func(self, *args, **kwargs)
                if not nested:
                    self.commit()
                return result
            except Exception as e:
                if nested and savepoint_name:
                    self.rollback_to_savepoint(savepoint_name)
                else:
                    self.rollback()
                raise e

        return wrapper

    return decorator
