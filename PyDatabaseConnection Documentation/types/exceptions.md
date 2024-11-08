# Database Connection Exceptions Documentation

## Overview
This document details the exception hierarchy used in the PyDatabaseConnection library. All exceptions inherit from the base `DatabaseError` class and provide specific error handling for different scenarios.

## Exception Hierarchy

### 1. DatabaseError
Base exception class for all database-related errors.

```python
try:
    # Database operations
except DatabaseError as e:
    print(f"Database error occurred: {e}")
    if e.details:
        print(f"Error details: {e.details}")
```

### 2. DatabaseConnectionError
Raised for connection-related issues.

```python
try:
    db.connect()
except DatabaseConnectionError as e:
    print(f"Failed to connect: {e}")
    # Connection parameters are safely masked in the details
    print(f"Connection attempt details: {e.details}")
```

### 3. DatabaseOperationError
Raised when database operations fail.

```python
try:
    db.execute("INSERT INTO users (name) VALUES (?)", ("John",))
except DatabaseOperationError as e:
    print(f"Operation failed: {e}")
    if 'query' in e.details:
        print(f"Failed query: {e.details['query']}")
```

### 4. ValidationError
Raised for parameter validation failures.

```python
try:
    db.with_params(port="invalid")
except ValidationError as e:
    print(f"Validation failed: {e}")
    if 'invalid_parameters' in e.details:
        print(f"Invalid parameters: {e.details['invalid_parameters']}")
```

### 5. TransactionError
Raised for transaction-related issues.

```python
try:
    with db.transaction():
        # Transaction operations
except TransactionError as e:
    print(f"Transaction failed: {e}")
    if 'transaction_state' in e.details:
        print(f"Transaction state: {e.details['transaction_state']}")
```

### 6. DataFrameOperationError
Raised for DataFrame operation failures.

```python
try:
    db.transform_dataframe('invalid_operation')
except DataFrameOperationError as e:
    print(f"DataFrame operation failed: {e}")
    if 'operation' in e.details:
        print(f"Failed operation: {e.details['operation']}")
```

### 7. CredentialError
Raised for credential-related issues.

```python
try:
    db.with_credentials_from_env()
except CredentialError as e:
    print(f"Credential error: {e}")
    # Username might be included in details if relevant
```

### 8. ConfigurationError
Raised for configuration-related issues.

```python
try:
    db.load_config()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    if 'configuration_key' in e.details:
        print(f"Problem with configuration key: {e.details['configuration_key']}")
```

### 9. TemplateError
Raised for template-related issues.

```python
try:
    db.get_template("INVALID_ENGINE")
except TemplateError as e:
    print(f"Template error: {e}")
    if 'template' in e.details:
        print(f"Problem with template: {e.details['template']}")
```

### 10. QueryError
Raised for SQL query-related issues.

```python
try:
    db.execute_sql_to_panda_dataframe("INVALID SQL")
except QueryError as e:
    print(f"Query error: {e}")
    if 'error_position' in e.details:
        print(f"Error at position: {e.details['error_position']}")
```

### 11. ExportError
Raised for data export failures.

```python
try:
    db.export_dataframe("invalid_format")
except ExportError as e:
    print(f"Export error: {e}")
    if 'format' in e.details:
        print(f"Problem with format: {e.details['format']}")
```

## Best Practices

### 1. Exception Handling
```python
def safe_database_operation():
    try:
        with DatabaseConnection("POSTGRESQL") as db:
            db.execute_sql_to_panda_dataframe("SELECT * FROM users")
    except DatabaseConnectionError as e:
        logger.error(f"Connection failed: {e}")
        raise
    except DatabaseOperationError as e:
        logger.error(f"Operation failed: {e}")
        raise
    except DatabaseError as e:
        logger.error(f"General database error: {e}")
        raise
```

### 2. Custom Exception Handling
```python
class CustomDatabaseHandler:
    def handle_error(self, error: DatabaseError) -> None:
        error_map = {
            DatabaseConnectionError: self._handle_connection_error,
            ValidationError: self._handle_validation_error,
            TransactionError: self._handle_transaction_error
        }
        
        handler = error_map.get(type(error), self._handle_generic_error)
        handler(error)
```

### 3. Error Recovery
```python
def retry_on_connection_error(max_attempts: int = 3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except DatabaseConnectionError as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
        return wrapper
    return decorator
```

## Integration with Logging

```python
import logging

logger = logging.getLogger(__name__)

def setup_error_logging():
    def log_error(error: DatabaseError):
        logger.error(f"{type(error).__name__}: {str(error)}")
        if error.details:
            logger.debug(f"Error details: {error.details}")

    return log_error
```

Would you like me to add more examples or elaborate on any specific aspect of the exception handling?