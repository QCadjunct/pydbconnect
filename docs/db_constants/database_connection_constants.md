# 🔌 Database Connection Constants Documentation

## 📑 Table of Contents
1. [Overview](#overview) [↩️](#table-of-contents)
2. [Helper Functions](#helper-functions) [↩️](#table-of-contents)
3. [Engine Configurations](#engine-configurations) [↩️](#table-of-contents)
4. [Engine-Specific Examples](#engine-specific-examples) [↩️](#table-of-contents)
5. [Usage Patterns](#usage-patterns) [↩️](#table-of-contents)

## 🎯 Overview

The `database_connection_constants.py` module defines configurations and connection parameters for different database engines. Each engine follows a template-based approach that ensures:

- ✨ Consistent configuration structure
- 🔒 Secure credential management
- 🔄 Dynamic module loading
- 🛠️ Engine-specific customization
- 📝 Clear parameter definitions

## 🛠️ Helper Functions

### Module Import
```python
def get_db_target_engine_module(module_name: str) -> Any:
    """
    Dynamically import database module.
    
    Args:
        module_name: Module to import (e.g., 'psycopg2', 'pyodbc')
        
    Returns:
        Imported module
        
    Raises:
        ImportError: If module not installed
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}. Make sure it's installed.") from e
```

### Parameter Loading
```python
def load_default_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load default parameters excluding sensitive data.
    
    Args:
        target_database_engine: Engine identifier
        d: Configuration dictionary
        
    Returns:
        Dictionary of non-sensitive parameters
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
    return {
        key: d[target_database_engine]["DEFAULT_PARAMETERS"][key]
        for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]
    }
```

[↩️ Back to Table of Contents](#table-of-contents)

## 🎨 Engine Configurations

Each database engine configuration follows this structure:

```python
ENGINE = {
    "ENGINE_NAME": {
        "DEFAULT_PARAMETERS": {
            # Connection basics
            "DRIVER": str,
            "DATABASE_NAME": str,
            "SERVER": str,
            "PORT_NUMBER": int,
            
            # Connection string formatting
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": List[str],
                "IS_DSN_NAME_SUPPORTED": bool,
                "BASE_CONNECTION_STRING": str
            }
        },
        "CRUDBASIC": {
            "IMPORT": str,               # Module to import
            "PARAMETER_PLACEHOLDER": str, # Query parameter style
            "IS_USERNAME_AND_PASSWORD_REQUIRED": bool
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": str,
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": Callable
        }
    }
}
```

[↩️ Back to Table of Contents](#table-of-contents)

## 🔧 Engine-Specific Examples

### MSSQL Configuration
```python
MSSQL = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "DSN_NAME": "Northwinds2024StudentDSN",
            "DATABASE_NAME": "Northwinds2024Student",
            "SERVER": "localhost",
            "PORT_NUMBER": 13001,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER", "DSN_NAME", "DATABASE_NAME", 
                    "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": (
                    "DRIVER={0}; SERVER={1},{2}; "
                    "DATABASE={3}; UID={4}; PWD={5};"
                )
            }
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}
```

### PostgreSQL Configuration
```python
POSTGRESQL = {
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{PostgreSQL ANSI(x64)}",
            "DSN_NAME": "PostgreSQL_DSN",
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER", "DSN_NAME", "DATABASE_NAME", 
                    "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": "Y",
                "BASE_CONNECTION_STRING": (
                    "DRIVER={0}; SERVER={1}; Port={2}; "
                    "DATABASE={3}; UID={4}; PWD={5};"
                )
            }
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True,
            "PARAMETER_PLACEHOLDER": "?"
        }
    }
}
```

[↩️ Back to Table of Contents](#table-of-contents)

## 📋 Usage Patterns

### Basic Connection
```python
# Load engine module
module_name = POSTGRESQL["POSTGRESQL"]["CRUDBASIC"]["IMPORT"]
db_module = get_db_target_engine_module(module_name)

# Get default parameters
params = load_default_parameter_keys_dict("POSTGRESQL", POSTGRESQL)

# Create connection string
conn_str = POSTGRESQL["POSTGRESQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
    params["DRIVER"],
    params["SERVER"],
    params["PORT_NUMBER"],
    params["DATABASE_NAME"],
    "username",  # From secure source
    "password"   # From secure source
)

# Connect
conn = db_module.connect(conn_str)
```

### DSN Connection
```python
def connect_with_dsn(engine_config: dict, dsn_name: str):
    """Connect using DSN if supported."""
    if not engine_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["IS_DSN_NAME_SUPPORTED"]:
        raise ValueError("DSN not supported for this engine")
        
    conn_str = engine_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
        dsn=dsn_name
    )
    
    module = get_db_target_engine_module(
        engine_config["CRUDBASIC"]["IMPORT"]
    )
    return module.connect(conn_str)
```

[↩️ Back to Table of Contents](#table-of-contents)

### Best Practices

1. **Secure Credentials**
   - Never hardcode credentials in configuration
   - Use environment variables or secure vaults
   - Exclude sensitive data from parameter loading

2. **Connection Management**
   - Close connections properly
   - Use connection pooling when supported
   - Handle connection errors gracefully

3. **DSN Usage**
   - Verify DSN support before using
   - Ensure DSN is properly configured
   - Fall back to direct connection if needed

[↩️ Back to Table of Contents](#table-of-contents)

# 🔌 Database Connection Constants

## 📚 Table of Contents
1. [Core Structure](#core-structure) [↩️](#table-of-contents)
2. [Engine Configurations](#engine-configurations) [↩️](#table-of-contents)
3. [Parameter Reference](#parameter-reference) [↩️](#table-of-contents)
4. [Connection Strings](#connection-strings) [↩️](#table-of-contents)
5. [Error Handling](#error-handling) [↩️](#table-of-contents)

## 🏗️ Core Structure

Each database engine configuration follows this template:

```python
ENGINE_NAME = {
    "ENGINE_NAME": {  # Matches TargetDatabaseEngine enum
        "DEFAULT_PARAMETERS": {
            # Core connection settings
            "DRIVER": str,
            "PORT_NUMBER": int,
            "SERVER": str,
            
            # Connection string formats
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": List[str],
                "IS_DSN_NAME_SUPPORTED": bool,
                "BASE_CONNECTION_STRING": str
            }
        },
        "CRUDBASIC": {
            "IMPORT": str,  # Module to import
            "PARAMETER_PLACEHOLDER": str,  # SQL parameter style
            "IS_USERNAME_AND_PASSWORD_REQUIRED": bool
        }
    }
}
```

[↩️ Back to Table of Contents](#table-of-contents)

## 🔧 Engine Configurations

### PostgreSQL (psycopg2)
```python
PSYCOPG2 = {
    "PSYCOPG2": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "postgres",
            "SERVER": "localhost",
            "PORT_NUMBER": 5432,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "SERVER", "PORT_NUMBER", "DATABASE_NAME"
                ],
                "IS_DSN_NAME_SUPPORTED": False,
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

### MSSQL
```python
MSSQL = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "SERVER": "localhost",
            "PORT_NUMBER": 1433,
            "DATABASE_NAME": "master",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER", "SERVER", "PORT_NUMBER", 
                    "DATABASE_NAME"
                ],
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": (
                    "DRIVER={0};SERVER={1},{2};"
                    "DATABASE={3};UID={4};PWD={5};"
                )
            }
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}
```

### SQLite3
```python
SQLITE3 = {
    "SQLITE3": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{SQLite3 ODBC Driver}",
            "DATABASE_NAME": ":memory:",  # Default to in-memory
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DATABASE_NAME"],
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "Database={0};"
            }
        },
        "CRUDBASIC": {
            "IMPORT": "sqlite3",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False
        }
    }
}
```

[↩️ Back to Table of Contents](#table-of-contents)

## 📝 Parameter Reference

### Connection Parameters
```python
class ConnectionParameters:
    """Common connection parameters across engines."""
    
    CORE_PARAMS = {
        "DRIVER": "Database driver name",
        "SERVER": "Database server hostname/IP",
        "PORT_NUMBER": "Database port number",
        "DATABASE_NAME": "Database/schema name"
    }
    
    AUTH_PARAMS = {
        "USERNAME": "Database username",
        "PASSWORD": "Database password",
        "UID": "User ID (alternative to USERNAME)",
        "PWD": "Password (alternative to PASSWORD)"
    }
    
    DSN_PARAMS = {
        "DSN_NAME": "Data Source Name identifier"
    }

def get_parameter_info(engine_type: TargetDatabaseEngine) -> Dict[str, str]:
    """Get parameter information for engine type."""
    config = get_engine_config(engine_type)
    params = {}
    
    # Get required parameters
    for key in config["DEFAULT_PARAMETERS"]["LOAD_DEFAULT_PARAMETER_KEYS"]:
        params[key] = ConnectionParameters.CORE_PARAMS.get(key, "")
    
    # Add auth if required
    if config["CRUDBASIC"]["IS_USERNAME_AND_PASSWORD_REQUIRED"]:
        params.update(ConnectionParameters.AUTH_PARAMS)
    
    # Add DSN if supported
    if config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["IS_DSN_NAME_SUPPORTED"]:
        params.update(ConnectionParameters.DSN_PARAMS)
    
    return params
```

[↩️ Back to Table of Contents](#table-of-contents)

## 🔗 Connection Strings

### Connection String Formatting
```python
def build_connection_string(
    engine_type: TargetDatabaseEngine,
    params: Dict[str, Any],
    use_dsn: bool = False
) -> str:
    """
    Build connection string for specified engine.
    
    Args:
        engine_type: Target database engine
        params: Connection parameters
        use_dsn: Whether to use DSN format
        
    Returns:
        Formatted connection string
    """
    config = get_engine_config(engine_type)
    format_config = config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]
    
    if use_dsn:
        if not format_config["IS_DSN_NAME_SUPPORTED"]:
            raise ValueError(f"DSN not supported for {engine_type}")
        return format_config["BASE_DSN_STRING"].format(**params)
        
    return format_config["BASE_CONNECTION_STRING"].format(**params)

# Examples:
# PostgreSQL
conn_str = build_connection_string(
    TargetDatabaseEngine.POSTGRESQL,
    {
        "SERVER": "localhost",
        "PORT_NUMBER": 5432,
        "DATABASE_NAME": "mydb",
        "USERNAME": "user",
        "PASSWORD": "pass"
    }
)

# MSSQL with DSN
conn_str = build_connection_string(
    TargetDatabaseEngine.MSSQL,
    {"DSN_NAME": "MyDSN"},
    use_dsn=True
)
```

[↩️ Back to Table of Contents](#table-of-contents)

## ⚠️ Error Handling

### Error Types
```python
class DatabaseError(Exception):
    """Base exception for database errors."""
    pass

class ConnectionStringError(DatabaseError):
    """Error in connection string formatting."""
    pass

class ParameterError(DatabaseError):
    """Error in connection parameters."""
    pass

class DriverError(DatabaseError):
    """Error with database driver."""
    pass
```

### Error Handling Patterns
```python
def safe_connect(
    engine_type: TargetDatabaseEngine,
    params: Dict[str, Any]
) -> Any:
    """
    Safely establish database connection.
    
    Args:
        engine_type: Target database engine
        params: Connection parameters
        
    Returns:
        Database connection
        
    Raises:
        DatabaseError: On connection failure
    """
    try:
        # Validate parameters
        config = get_engine_config(engine_type)
        if not all(
            key in params 
            for key in config["DEFAULT_PARAMETERS"]["LOAD_DEFAULT_PARAMETER_KEYS"]
        ):
            raise ParameterError("Missing required parameters")
        
        # Build connection string
        conn_str = build_connection_string(engine_type, params)
        
        # Import module
        module_name = config["CRUDBASIC"]["IMPORT"]
        try:
            module = get_db_target_engine_module(module_name)
        except ImportError as e:
            raise DriverError(f"Failed to load driver: {e}")
        
        # Establish connection
        return module.connect(conn_str)
        
    except Exception as e:
        raise DatabaseError(f"Connection failed: {str(e)}")
```

[↩️ Back to Table of Contents](#table-of-contents)

