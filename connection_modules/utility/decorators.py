'''' pydatabaseconnection/utils/decorators.py '''

from functools import wraps
from typing import Any, Callable, Type, TypeVar
import logging
from time import time

T = TypeVar('T')

def log_operation(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log database operations."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time()
        logger = logging.getLogger(func.__module__)
        logger.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed {func.__name__} in {time() - start_time:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

def retry_on_error(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    """Decorator to retry operations on failure."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

def validate_connection(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate database connection before operation."""
    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> T:
        if not hasattr(self, '_connection') or self._connection is None:
            raise ConnectionError("Database connection not established")
        return func(self, *args, **kwargs)
    return wrapper

def transaction(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to wrap operation in transaction."""
    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> T:
        try:
            result = func(self, *args, **kwargs)
            self._connection.commit()
            return result
        except Exception as e:
            self._connection.rollback()
            raise ExecutionError(f"Transaction failed: {str(e)}")
    return wrapper