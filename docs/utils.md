# pydbconnect Utilities Documentation

This module provides core utilities for the pydbconnect package, focusing on parameter handling and connection validation.

## Decorators

### `preload_default_parameters`

Manages parameter merging for database connections, ensuring proper default and custom parameter handling.

```python
from pydbconnect.utils import preload_default_parameters

class DatabaseConnection:
    def get_default_params(self):
        return {"host": "localhost", "port": 5432}

    @preload_default_parameters(get_default_params)
    def connect(self, **kwargs):
        # kwargs contains merged default and custom parameters
        pass
```

**Error Handling:**

- Validates callable status of preloaded_params_method
- Ensures return value is dictionary
- Validates required parameters are present

### `ensure_connected`

Verifies database connection exists before executing database operations.

```python
from pydbconnect.utils import ensure_connected

class DatabaseConnection:
    @ensure_connected
    def execute_query(self, query):
        # Connection is guaranteed to exist
        pass
```

**Error Handling:**

- Raises ConnectionError if database not connected

## Utility Functions

### `validate_connection_params`

Validates presence of required connection parameters.

```python
from pydbconnect.utils import validate_connection_params

# Example usage
params = {"host": "localhost", "port": 5432}
required = {"host", "port", "database"}
validate_connection_params(params, required)  # Raises ValueError
```

**Error Handling:**

- Raises ValueError if required parameters missing

## Best Practices

1. **Parameter Validation**
   - Always validate parameters before connection attempts
   - Use type hints for better code clarity
   - Handle missing parameters gracefully

2. **Connection Management**
   - Use ensure_connected decorator for database operations
   - Validate connection state before critical operations
   - Clean up resources properly

3. **Error Handling**
   - Catch and handle specific exceptions
   - Provide clear error messages
   - Maintain connection state integrity

## Example Usage

```python
from pydbconnect.utils import preload_default_parameters, ensure_connected

class DatabaseConnection:
    def get_default_params(self):
        return {
            "host": "localhost",
            "port": 5432,
            "database": "mydb"
        }

    @preload_default_parameters(get_default_params)
    def connect(self, **kwargs):
        # Parameters are automatically merged and validated
        pass

    @ensure_connected
    def execute_query(self, query):
        # Connection is verified before execution
        return self._connection.execute(query)
```
