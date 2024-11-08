# Database Connection Decorators Documentation

## Overview
## This module provides decorators for enhancing database connection operations 
## with parameter handling, logging, validation, and error handling capabilities.

## Decorators

### 1. preload_default_parameters
```python
@preload_default_parameters(get_default_params_method)
def method(self, **custom_params):
    pass
```

**Purpose**: Merges default parameters with custom parameters while maintaining the fluent interface pattern.

**Parameters**:
- `get_default_params_method`: Method that returns default parameters dictionary

**Usage Example**:
```python
def _get_default_parameters(self) -> Dict[str, Any]:
    return self._default_params

@preload_default_parameters(_get_default_parameters)
def connect(self, **custom_params):
    final_params = custom_params  # Already merged with defaults
    return self.create_connection(final_params)
```

### 2. log_execution
```python
@log_execution(logger=None)
def method(self, *args, **kwargs):
    pass
```

**Purpose**: Logs method execution time and status.

**Parameters**:
- `logger`: Optional custom logger instance

**Usage Example**:
```python
@log_execution()
def execute_query(self, query: str):
    return self._connection.execute(query)
```

### 3. validate_connection
```python
@validate_connection
def method(self, *args, **kwargs):
    pass
```

**Purpose**: Ensures database connection exists before method execution.

**Usage Example**:
```python
@validate_connection
def execute_query(self, query: str):
    return self._connection.execute(query)
```

### 4. retry
```python
@retry(max_attempts=3, delay=1.0)
def method(self, *args, **kwargs):
    pass
```

**Purpose**: Implements retry logic with exponential backoff.

**Parameters**:
- `max_attempts`: Maximum number of retry attempts
- `delay`: Initial delay between retries (doubles with each attempt)

**Usage Example**:
```python
@retry(max_attempts=3)
def connect(self):
    return self._establish_connection()
```

### 5. deprecated
```python
@deprecated(message="Use new_method instead")
def old_method(self):
    pass
```

**Purpose**: Marks methods as deprecated with optional message.

**Parameters**:
- `message`: Custom deprecation message

**Usage Example**:
```python
@deprecated("Use execute_query instead")
def query(self, sql: str):
    return self.execute_query(sql)
```

### 6. cache_result
```python
@cache_result(maxsize=128)
def method(self, *args, **kwargs):
    pass
```

**Purpose**: Caches method results with LRU (Least Recently Used) strategy.

**Parameters**:
- `maxsize`: Maximum cache size

**Usage Example**:
```python
@cache_result(maxsize=256)
def get_metadata(self, table_name: str):
    return self._fetch_metadata(table_name)
```

## Decorator Combinations

Decorators can be combined to provide multiple features:

```python
@log_execution()
@validate_connection
@retry(max_attempts=3)
def execute_complex_query(self, query: str):
    return self._connection.execute(query)
```

## Best Practices

1. **Order Matters**: When combining decorators, consider their execution order:
   - Validation decorators should usually come first
   - Logging decorators should wrap other decorators
   - Retry decorators should be closest to the method

2. **Error Handling**: Decorators include proper error handling and logging:
   ```python
   try:
       result = method(*args, **kwargs)
       return result
   except Exception as e:
       logging.error(f"Method failed: {str(e)}")
       raise
   ```

3. **Type Hints**: Decorators maintain proper type hints for better IDE support:
   ```python
   from typing import TypeVar, Callable
   
   ReturnType = TypeVar('ReturnType')
   
   def decorator(
       method: Callable[..., ReturnType]
   ) -> Callable[..., ReturnType]:
       pass
   ```

4. **Documentation**: Each decorated method should include appropriate docstrings:
   ```python
   @validate_connection
   def execute_query(self, query: str) -> Any:
       """
       Execute SQL query with connection validation.
       
       Args:
            query: SQL query to execute
            
       Returns:
            Query results
            
       Raises:
            ConnectionError: If database connection is not established
       """
       return self._connection.execute(query)
