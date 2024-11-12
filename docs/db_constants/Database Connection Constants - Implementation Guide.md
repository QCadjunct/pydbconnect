
# 🔧 Database Connection Constants - Implementation Guide

## Table of Contents
1. [Parameter Validation](#parameter-validation) [↩️](#table-of-contents)
2. [Connection Templates](#connection-templates) [↩️](#table-of-contents)
3. [Error Handling](#error-handling) [↩️](#table-of-contents)

## Parameter Validation 🔍

### Basic Parameter Validation
```python
def validate_connection_params(params: Dict[str, Any], engine_config: Dict) -> Dict[str, Any]:
    """
    Validate connection parameters against engine configuration.
    Maps directly to engine configuration requirements.
    """
    required_params = engine_config["DEFAULT_PARAMETERS"]["REQUIRED_PARAMS"]
    optional_params = engine_config["DEFAULT_PARAMETERS"]["OPTIONAL_PARAMS"]
    
    # Check required parameters
    missing = [param for param in required_params if param not in params]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")
    
    # Remove unknown parameters
    valid_params = set(required_params + optional_params)
    return {k: v for k, v in params.items() if k in valid_params}
```

### Type-Safe Parameter Validation
```python
from typing import TypedDict, Literal

class SSLParams(TypedDict, total=False):
    mode: Literal["disable", "require", "verify-ca", "verify-full"]
    cert: str
    key: str
    ca: str

class ConnectionParams(TypedDict):
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl: Optional[SSLParams]

def validate_typed_params(params: ConnectionParams, engine_config: Dict) -> ConnectionParams:
    """Type-safe parameter validation."""
    validated = validate_connection_params(params, engine_config)
    
    # Validate SSL if present
    if ssl_params := validated.get('ssl'):
        validate_ssl_params(ssl_params, engine_config)
        
    return ConnectionParams(**validated)
```

[↩️ Back to Table of Contents](#table-of-contents)


## Connection Templates 🔗

### Basic Templates
```python
CONNECTION_TEMPLATES = {
    "DEFAULT": {
        "standard": (
            "DRIVER={driver};"
            "SERVER={host};"
            "PORT={port};"
            "DATABASE={database};"
            "UID={username};"
            "PWD={password}"
        ),
        "dsn": "DSN={dsn_name};UID={username};PWD={password}"
    },
    
    "WINDOWS_AUTH": {
        "standard": (
            "DRIVER={driver};"
            "SERVER={host};"
            "DATABASE={database};"
            "Trusted_Connection=yes"
        )
    },
    
    "SSL": {
        "standard": (
            "DRIVER={driver};"
            "SERVER={host};"
            "DATABASE={database};"
            "UID={username};"
            "PWD={password};"
            "SSL=true;"
            "SSLCert={ssl_cert};"
            "SSLKey={ssl_key};"
            "SSLRootCert={ssl_ca}"
        )
    }
}

def get_connection_string(template_type: str, params: Dict[str, Any]) -> str:
    """Get formatted connection string from template."""
    try:
        template = CONNECTION_TEMPLATES[template_type]["standard"]
        return template.format(**params)
    except KeyError as e:
        raise ValueError(f"Invalid parameter or template: {e}")
```

### Template Usage Examples
```python
# Standard connection
standard_params = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "host": "localhost",
    "port": 1433,
    "database": "master",
    "username": "sa",
    "password": "password"
}
conn_str = get_connection_string("DEFAULT", standard_params)

# Windows authentication
windows_params = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "host": "localhost",
    "database": "master"
}
win_auth_str = get_connection_string("WINDOWS_AUTH", windows_params)

# SSL connection
ssl_params = {
    "driver": "{PostgreSQL UNICODE}",
    "host": "db.example.com",
    "database": "myapp",
    "username": "user",
    "password": "pass",
    "ssl_cert": "/path/to/client-cert.pem",
    "ssl_key": "/path/to/client-key.pem",
    "ssl_ca": "/path/to/server-ca.pem"
}
ssl_conn_str = get_connection_string("SSL", ssl_params)
```

[↩️ Back to Table of Contents](#table-of-contents)

## Error Handling ⚠️

### Structured Error Handling
```python
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Connection-related errors."""
    def __init__(self, message: str, params: Optional[Dict] = None):
        self.params = params  # Store safe copy of parameters
        super().__init__(message)

class ValidationError(DatabaseError):
    """Parameter validation errors."""
    pass

def create_connection(engine_config: Dict, params: Dict[str, Any]) -> Any:
    """
    Create database connection with comprehensive error handling.
    Maps directly to engine configuration structure.
    """
    try:
        # Validate parameters
        validated_params = validate_connection_params(params, engine_config)
        
        # Get connection string
        template_type = "SSL" if validated_params.get('ssl') else "DEFAULT"
        conn_str = get_connection_string(template_type, validated_params)
        
        # Import module
        module_name = engine_config["RUNTIME"]["MODULE"]
        module = get_db_target_engine_module(module_name)
        
        # Create connection
        return module.connect(conn_str)
        
    except ImportError as e:
        raise ConnectionError(
            f"Failed to import database module: {module_name}",
            {"module": module_name}
        ) from e
        
    except Exception as e:
        # Create safe parameter copy without credentials
        safe_params = {
            k: v for k, v in params.items()
            if k not in {'password', 'pwd', 'PWD'}
        }
        raise ConnectionError(
            f"Failed to create connection: {str(e)}",
            safe_params
        ) from e
```

### Error Recovery Examples
```python
def connect_with_retry(engine_config: Dict, 
                      params: Dict[str, Any], 
                      max_retries: int = 3, 
                      delay: int = 5) -> Any:
    """Create connection with retry logic."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return create_connection(engine_config, params)
        except ConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(delay)
            continue
    
    raise last_error

def get_safe_connection(engine_config: Dict, 
                       params: Dict[str, Any]) -> Any:
    """Get connection with automatic cleanup on error."""
    conn = None
    try:
        conn = create_connection(engine_config, params)
        return conn
    except Exception:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        raise
```

[↩️ Back to Table of Contents](#table-of-contents)

