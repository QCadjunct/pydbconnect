"""Utility decorators."""

from typing import Any, Callable, Optional
from functools import wraps
import time
import logging
from datetime import datetime
from templates.constraints import IsolationLevel  # Ensure this import is correct


def preload_parameters(preload_method: Callable) -> Callable:
    """
    Decorator that preloads default parameters and merges them with custom parameters.
    """

    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, **params: Any) -> Any:
            if not callable(preload_method):
                raise ValueError("preload_method must be callable")

            default_params = preload_method(self)
            if not isinstance(default_params, dict):
                raise TypeError("preload_method must return a dictionary")

            merged_params = default_params.copy()
            merged_params.update(params)

            return method(self, **merged_params)

        return wrapper

    return decorator


def ensure_connected(f: Callable) -> Callable:
    """
    Decorator to ensure database connection exists before executing a method.
    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        # Check for direct connection
        if hasattr(self, "_connection") and self._connection is not None:
            return f(self, *args, **kwargs)
        # Check for connector
        if hasattr(self, "connector") and self.connector.is_database_active:
            return f(self, *args, **kwargs)
        raise RuntimeError("Database connection not established")  # Generic error

    return wrapper


def with_isolation_level(isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
    """Decorator for setting isolation level with process awareness."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            import os

            pid = os.getpid()
            session_id = getattr(self._connection, "spid", None)  # For SQL Server

            original_level = self._current_isolation
            try:
                if session_id:
                    # Log the session info
                    logging.info(f"Setting isolation level for PID {pid}, Session {session_id}")
                self._current_isolation = isolation_level
                return func(self, *args, **kwargs)
            finally:
                self._current_isolation = original_level

        return wrapper

    return decorator


def transactional(nested: bool = False):
    """Decorator for transaction control."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @ensure_connected
        def wrapper(self, *args, **kwargs):
            if not nested and self._transaction_active:
                raise DatabaseError("Transaction already active and nested=False")

            try:
                self.begin_transaction()
                result = func(self, *args, **kwargs)
                self.commit()
                return result
            except Exception:
                self.rollback()
                raise

        return wrapper

    return decorator


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for operation retry logic."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception: Optional[BaseException] = None
            for attempt in range(max_attempts):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue
            if last_exception is not None:
                raise last_exception
            else:
                raise RuntimeError("Operation failed without raising an exception")

        return wrapper

    return decorator


def log_operation(operation_name: Optional[str] = None):
    """Decorator for operation logging."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = datetime.now()

            try:
                result = func(self, *args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                logging.info(f"Operation {op_name} completed successfully in {duration:.2f}s")
                return result

            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                logging.error(f"Operation {op_name} failed after {duration:.2f}s: {str(e)}")
                raise

        return wrapper

    return decorator
