# Database Connection Constants Documentation

## Table of Contents
1. [Overview](#overview)
2. [Helper Functions](#helper-functions)
3. [Database Engine Configurations](#database-engine-configurations)
4. [Common Usage Patterns](#common-usage-patterns)
5. [Engine-Specific Examples](#engine-specific-examples)
6. [Advanced Use Cases](#advanced-use-cases)

## Overview

This module defines database engine configurations and constants used for database connections. It provides a template-based approach for managing different database engines, their configurations, and connection parameters.

### Key Features
- 🔌 Template-based engine configurations
- 🔒 Secure credential management
- 🔄 DSN and direct connection support
- 🛠️ Extensible design for new engines
- 📝 Consistent parameter handling

## Helper Functions

### Module Import Helper
```python
def get_db_target_engine_module(module_name: str) -> Any:
    """
    Dynamically import a database module.

    Args:
        module_name (str): Name of the module to import (e.g., 'psycopg2', 'pyodbc')

    Returns:
        Any: The imported module

    Raises:
        ImportError: If module import fails
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}") from e

# Usage
psycopg2 = get_db_target_engine_module('psycopg2')
```

### Parameter Management
```python
def load_default_parameter_keys_dict(
    target_database_engine: str, 
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Load default parameters excluding sensitive data.
    
    Args:
        target_database_engine: Database engine identifier
        config: Engine configuration dictionary
        
    Returns:
        Dict containing non-sensitive parameters
    """
    format_config = config[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]
    keys = format_config["LOAD_DEFAULT_PARAMETER_KEYS"]
    return {
        key: config[target_database_engine]["DEFAULT_PARAMETERS"][key]
        for key in keys if key not in ["USERNAME", "PASSWORD", "UID", "PWD"]
    }
```

## Database Engine Configurations

### Base Configuration Template
```python
ENGINE_TEMPLATE = {
    "DEFAULT_PARAMETERS": {
        "FORMAT_CONNECTION_STRING": {
            "LOAD_DEFAULT_PARAMETER_KEYS": [],
            "IS_DSN_NAME_SUPPORTED": bool,
            "BASE_CONNECTION_STRING": str,
        }
    },
    "CRUDBASIC": {
        "IMPORT": str,
        "PARAMETER_PLACEHOLDER": str,
        "IS_USERNAME_AND_PASSWORD_REQUIRED": bool
    },
    "CREATE_DATABASE_CONNECTION": {
        "CONNECTION_NOTES": str,
        "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": callable
    }
}
```

### Example: PostgreSQL Configuration
```python
POSTGRESQL = {
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{PostgreSQL ANSI}",
            "SERVER": "localhost",
            "PORT": 5432,
            "DATABASE": "postgres",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER", "SERVER", "PORT", "DATABASE"
                ],
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": (
                    "host={0} port={1} dbname={2} "
                    "user={3} password={4}"
                )
            }
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg2",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}
```

## Common Usage Patterns

### Basic Connection Setup
```python
def create_connection(engine_config: dict) -> Any:
    """Create database connection using configuration."""
    connection_string = build_connection_string(engine_config)
    module = get_db_target_engine_module(
        engine_config["CRUDBASIC"]["IMPORT"]
    )
    return module.connect(connection_string)

# Usage
conn = create_connection(POSTGRESQL["POSTGRESQL"])
```

### Parameter Loading
```python
def load_connection_params(engine_config: dict) -> dict:
    """Load connection parameters from config."""
    params = engine_config["DEFAULT_PARAMETERS"].copy()
    
    # Remove sensitive data
    sensitive_keys = {"USERNAME", "PASSWORD", "UID", "PWD"}
    return {
        k: v for k, v in params.items()
        if k not in sensitive_keys
    }

# Usage
params = load_connection_params(POSTGRESQL["POSTGRESQL"])
```

## Engine-Specific Examples

### MySQL Connection
```python
def mysql_connection() -> Any:
    """Create MySQL connection with SSL."""
    config = MYSQL["MYSQL"].copy()
    config["DEFAULT_PARAMETERS"].update({
        "SSL_MODE": "REQUIRED",
        "SSL_CA": "/path/to/ca.pem"
    })
    
    return create_connection(config)
```

### MSSQL with Windows Auth
```python
def mssql_windows_auth() -> Any:
    """Create MSSQL connection using Windows authentication."""
    config = MSSQL["MSSQL"].copy()
    config["DEFAULT_PARAMETERS"].update({
        "Trusted_Connection": "yes",
        "IS_USERNAME_AND_PASSWORD_REQUIRED": False
    })
    
    return create_connection(config)
```

## Advanced Use Cases

### Connection Pool Implementation
```python
class ConnectionPool:
    """Manage database connection pool."""
    
    def __init__(self, engine_config: dict, pool_size: int = 5):
        self.config = engine_config
        self.pool_size = pool_size
        self.connections = []

    def get_connection(self) -> Any:
        """Get connection from pool or create new one."""
        if not self.connections:
            return create_connection(self.config)
        return self.connections.pop()

    def return_connection(self, conn: Any) -> None:
        """Return connection to pool."""
        if len(self.connections) < self.pool_size:
            self.connections.append(conn)
        else:
            conn.close()

# Usage
pool = ConnectionPool(POSTGRESQL["POSTGRESQL"])
with pool.get_connection() as conn:
    # Use connection
    pass
```

### Multi-Database Manager
```python
class MultiDBManager:
    """Manage multiple database connections."""
    
    def __init__(self):
        self.connections = {}

    def add_connection(self, name: str, config: dict) -> None:
        """Add new database connection."""
        self.connections[name] = create_connection(config)

    def execute_query(self, db_name: str, query: str) -> Any:
        """Execute query on specified database."""
        conn = self.connections.get(db_name)
        if not conn:
            raise ValueError(f"No connection for {db_name}")
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

# Usage
manager = MultiDBManager()
manager.add_connection("postgres", POSTGRESQL["POSTGRESQL"])
manager.add_connection("mysql", MYSQL["MYSQL"])
```