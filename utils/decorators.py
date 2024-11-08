from typing import Dict, Any, Callable, TypeVar, Union, Optional
from functools import wraps
import logging
from datetime import datetime

# Type variables for generic decorators
T = TypeVar('T')
ReturnType = TypeVar('ReturnType')

def preload_default_parameters(get_default_params_method: Callable[[], Dict[str, Any]]):
    """
    Decorator that preloads default parameters and merges them with custom parameters.
    Handles parameter merging while maintaining the fluent interface pattern.
    """
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, use_default_parameters: bool = True, **custom_params: Any):
            try:
                # Get default parameters from the provided method
                default_params = get_default_params_method(self)
                
                if use_default_parameters:
                    # Merge defaults with custom parameters
                    final_params = default_params.copy()
                    final_params.update(custom_params)
                else:
                    # Use only custom parameters
                    final_params = custom_params

                # Call the original method with merged parameters
                return method(self, **final_params)
            except Exception as e:
                # Log the error and re-raise with more context
                logging.error(f"Parameter loading failed: {str(e)}")
                raise type(e)(
                    f"Failed to load parameters in {method.__name__}: {str(e)}"
                )
        return wrapper
    return decorator

def log_execution(logger: Optional[logging.Logger] = None):
    """
    Decorator to log method execution with timing information.
    """
    def decorator(method: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        @wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            _logger = logger or logging.getLogger(method.__module__)
            start_time = datetime.now()
            
            try:
                result = method(*args, **kwargs)
                execution_time = datetime.now() - start_time
                
                _logger.info(
                    f"Method {method.__name__} completed in {execution_time.total_seconds():.2f} seconds"
                )
                return result
                
            except Exception as e:
                execution_time = datetime.now() - start_time
                _logger.error(
                    f"Method {method.__name__} failed after {execution_time.total_seconds():.2f} seconds: {str(e)}"
                )
                raise
        return wrapper
    return decorator

def validate_connection(method: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
    """
    Decorator to validate database connection before executing a method.
    """
    @wraps(method)
    def wrapper(self, *args: Any, **kwargs: Any) -> ReturnType:
        if not hasattr(self, '_connection') or self._connection is None:
            raise ConnectionError(
                f"Database connection required for {method.__name__}"
            )
        return method(self, *args, **kwargs)
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry a method on failure with exponential backoff.
    """
    def decorator(method: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        @wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            from time import sleep
            
            for attempt in range(max_attempts):
                try:
                    return method(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    
                    sleep_time = delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(
                        f"Attempt {attempt + 1} failed for {method.__name__}: {str(e)}. "
                        f"Retrying in {sleep_time} seconds..."
                    )
                    sleep(sleep_time)
            
            raise RuntimeError(f"All {max_attempts} attempts failed for {method.__name__}")
        return wrapper
    return decorator

def deprecated(message: str = ""):
    """
    Decorator to mark methods as deprecated.
    """
    def decorator(method: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        @wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            warning_message = (
                f"Method {method.__name__} is deprecated. "
                f"{message if message else 'It will be removed in a future version.'}"
            )
            import warnings
            warnings.warn(warning_message, DeprecationWarning, stacklevel=2)
            return method(*args, **kwargs)
        return wrapper
    return decorator

def cache_result(maxsize: int = 128):
    """
    Decorator to cache method results.
    """
    from functools import lru_cache
    
    def decorator(method: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        # Create cache for the method
        method_cache = lru_cache(maxsize=maxsize)(method)
        
        @wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            try:
                return method_cache(*args, **kwargs)
            except TypeError:  # If arguments are not hashable
                return method(*args, **kwargs)
        
        # Add cache info method to wrapper
        wrapper.cache_info = method_cache.cache_info
        wrapper.cache_clear = method_cache.cache_clear
        return wrapper
    return decorator

