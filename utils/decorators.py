"""Utility decorators."""

from typing import Dict, Any, Callable
from functools import wraps


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
        if not hasattr(self, "_connection") or self._connection is None:
            raise RuntimeError("Database connection not established")  # Generic error
        return f(self, *args, **kwargs)

    return wrapper
