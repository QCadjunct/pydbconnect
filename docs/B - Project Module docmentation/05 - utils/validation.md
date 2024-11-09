

# Validation System Documentation

## Overview
The validation system provides comprehensive validation for database connections, parameters, queries, and DataFrame operations. It consists of four main components:
- ValidationRules: Core validation rules and constraints
- ConnectionValidator: Connection parameter and credential validation
- QueryValidator: SQL query and parameter validation
- DataFrameValidator: DataFrame operation validation

## 1. ValidationRules

### 1.1 Constants and Rules
```python
PORT_RANGE = (1, 65535)
MAX_USERNAME_LENGTH = 128
MAX_PASSWORD_LENGTH = 256
VALID_HOSTNAME_REGEX = r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
RESERVED_WORDS = {'select', 'drop', 'delete', 'update', 'insert', 'alter', 'truncate'}
```

### 1.2 Methods
```python
# Validate port number
is_valid_port(port: int) -> bool

# Validate hostname/server
is_valid_hostname(hostname: str) -> bool

# Validate IP address
is_valid_ip(ip: str) -> bool

# Validate database name
is_valid_database_name(name: str) -> bool
```

## 2. Connection Validation

### 2.1 Parameter Validation
```python
# Validate connection parameters
ConnectionValidator.validate_connection_params(
    params: Dict[str, Any],
    required_params: Set[str]
)

# Example usage:
validator.validate_connection_params({
    'SERVER': 'localhost',
    'PORT_NUMBER': 1433,
    'DATABASE_NAME': 'mydb'
}, {'SERVER', 'PORT_NUMBER'})
```

### 2.2 Credential Validation
```python
# Validate credentials
ConnectionValidator.validate_credentials(
    username: Optional[str],
    password: Optional[str],
    required: bool = True
)

# Example usage:
validator.validate_credentials('user', 'pass', required=True)
```

## 3. Query Validation

### 3.1 SQL Query Validation
```python
# Validate SQL query
QueryValidator.validate_query(query: str)

# Example usage:
validator.validate_query("""
    SELECT * FROM users 
    WHERE username = ? AND status = ?
""")
```

### 3.2 Parameter Validation
```python
# Validate query parameters
QueryValidator.validate_parameters(
    params: Union[tuple, list, dict, None],
    expected_count: int
)

# Example usage:
validator.validate_parameters(
    ('user1', 'active'),
    expected_count=2
)
```

## 4. DataFrame Validation

### 4.1 DataFrame Operation Validation
```python
# Validate DataFrame for operations
DataFrameValidator.validate_dataframe_operation(
    df: Any,
    required_columns: Optional[List[str]] = None,
    min_rows: int = 0
)

# Example usage:
validator.validate_dataframe_operation(
    df,
    required_columns=['id', 'value'],
    min_rows=1
)
```

### 4.2 Transform Operation Validation
```python
# Validate transformation operation
DataFrameValidator.validate_transform_operation(
    transform: Union[str, callable],
    allowed_transforms: Set[str]
)

# Example usage:
validator.validate_transform_operation(
    'standardize',
    {'standardize', 'normalize', 'fillna'}
)
```

## 5. Usage Examples

### 5.1 Connection Validation Example
```python
try:
    # Validate connection parameters
    ConnectionValidator.validate_connection_params({
        'SERVER': 'localhost',
        'PORT_NUMBER': 1433,
        'DATABASE_NAME': 'mydb'
    }, {'SERVER', 'PORT_NUMBER'})
    
    # Validate credentials
    ConnectionValidator.validate_credentials(
        username='myuser',
        password='mypass'
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 5.2 Query Validation Example
```python
try:
    # Validate query
    query = "SELECT * FROM users WHERE status = ?"
    params = ('active',)
    
    QueryValidator.validate_query(query)
    QueryValidator.validate_parameters(params, 1)
    
except ValidationError as e:
    print(f"Query validation failed: {e}")
```

### 5.3 DataFrame Validation Example
```python
try:
    # Validate DataFrame
    DataFrameValidator.validate_dataframe_operation(
        df,
        required_columns=['id', 'name', 'value'],
        min_rows=1
    )
    
    # Validate transformation
    DataFrameValidator.validate_transform_operation(
        'standardize',
        {'standardize', 'normalize'}
    )
    
except ValidationError as e:
    print(f"DataFrame validation failed: {e}")
```

## 6. Error Handling

### 6.1 ValidationError
All validation methods raise `ValidationError` with descriptive messages:

```python
class ValidationError(Exception):
    """Base exception for validation errors"""
    pass

# Error handling example
try:
    ConnectionValidator.validate_connection_params(params, required_params)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    # Handle error appropriately
```

### 6.2 Common Validation Errors
- Missing required parameters
- Invalid port numbers
- Invalid hostnames/IPs
- Invalid database names
- Invalid credentials
- Dangerous SQL patterns
- Parameter count mismatches
- Invalid DataFrame operations

## 7. Best Practices

1. Always validate connection parameters before attempting connection
2. Use parameterized queries instead of string concatenation
3. Validate credentials when authentication is required
4. Validate DataFrame operations before processing
5. Handle validation errors appropriately
6. Log validation failures for debugging
7. Use type hints for better code clarity
8. Keep validation rules updated with security best practices