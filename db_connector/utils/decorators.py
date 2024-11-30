"""Utility decorators."""

from typing import Dict, Any, Callable
from functools import wraps
from inspect import signature


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
        def wrapper(self, **custom_params: Any) -> Any:
            # Validate method exists and returns dict
            if not callable(preload_method):
                raise ValueError("preload_method must be callable")

            # Get default parameters
            default_params = preload_method(self)
            if not isinstance(default_params, dict):
                raise TypeError("preload_method must return a dictionary")

            # Merge parameters, with custom taking precedence
            merged_params = default_params.copy()
            merged_params.update(custom_params)

            # Validate required parameters
            sig = signature(method)
            required_params = {
                name
                for name, param in sig.parameters.items()
                if param.default == param.empty and param.name != "self"
            }
            missing_params = required_params - merged_params.keys()
            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")

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
