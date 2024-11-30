# 🎯 Database Target Engine Module Documentation
[//]: # "Database Engine Implementation, Constraints & Examples"

## 📑 Table of Contents
- [Overview](#overview)
- [Core Implementation](#core-implementation)
- [Validation Constraints](#validation-constraints)
- [Examples](#examples)
- [Testing](#testing)
- [Error Handling](#error-handling)

<a name="overview"></a>
## 🔍 Overview 

The `TargetDatabaseEngine` module provides a robust enumeration system for managing database connections with built-in validation and configuration management. The cornerstone of this implementation is the self-documenting `target_database_engine_name` attribute.

### Key Features
- ✨ Self-documenting engine identification
- 🔒 Built-in validation constraints
- 🔄 Consistent naming conventions
- 🛠️ Comprehensive error handling

<a name="core-implementation"></a>
## 💻 Core Implementation

### Database Engine Enumeration
```python
from enum import Enum
from typing import Dict, Any, Type
from abc import ABC, abstractmethod
import importlib

class TargetDatabaseEngine(Enum):
    """Database engines supported by pydbconnect."""
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

    def __init__(self, value: str):
        """Initialize enum with target database engine name."""
        self._value_ = value
        self.target_database_engine_name = self.name

    @property
    def target_database_engine_name(self) -> str:
        """Get the name of the target database engine."""
        return self.name
```

### Engine Configuration Management
```python
def load_engine_config(self) -> Dict[str, Any]:
    """Load complete engine configuration."""
    return getattr(template, self.target_database_engine_name)

def get_placeholder(self) -> str:
    """Get SQL parameter placeholder for this engine."""
    engine_config = self.load_engine_config()
    return engine_config.get('CRUDBASIC', {}).get('PARAMETER_PLACEHOLDER', '?')
```

<a name="validation-constraints"></a>
## ✅ Validation Constraints

### Authentication Validation
```python
@property
def requires_authentication(self) -> bool:
    """
    Check if engine requires username/password authentication.
    Gets value from engine configuration.
    """
    engine_config = getattr(template, self.target_database_engine_name)
    return engine_config.get('REQUIRES_CREDENTIALS', False)
```

### DSN Support Validation
```python
@property
def supports_dsn(self) -> bool:
    """
    Check if engine supports DSN connections.
    Gets value from engine configuration.
    """
    engine_config = getattr(template, self.target_database_engine_name)
    return engine_config.get('FORMAT_CONNECTION_STRING', {}).get(
        'IS_DSN_NAME_SUPPORTED', False
    )
```

### Connection Option Validation
```python
def validate_connection_option(self, option: 'TargetDatabaseConnectionStringOption') -> bool:
    """Validate connection option compatibility."""
    # DSN validation
    if option.uses_dsn and not self.supports_dsn:
        return False
        
    # Authentication validation
    if option.changes_credentials and not self.requires_authentication:
        return False
        
    return True
```

<a name="examples"></a>
## 🚀 Examples

### 1. Basic Database Connection
```python
def setup_database_connection():
    # Initialize engine
    engine = TargetDatabaseEngine.MYSQL
    
    # Validate and configure
    if engine.requires_authentication:
        credentials_valid = validate_credentials("user", "pass")
        if not credentials_valid:
            raise DatabaseConnectionError("Invalid credentials")
            
    # Load configuration
    config = engine.load_engine_config()
    
    return create_connection(engine, config)
```

### 2. Advanced Connection String Handling
```python
def create_connection_string(
    engine: TargetDatabaseEngine,
    option: TargetDatabaseConnectionStringOption,
    **kwargs
) -> str:
    """Create appropriate connection string based on engine and option."""
    
    # Validate compatibility
    if not engine.validate_connection_option(option):
        raise InvalidConnectionOptionError(engine, option)
    
    # Handle DSN connections
    if option.uses_dsn:
        if not engine.supports_dsn:
            raise InvalidConnectionOptionError(
                f"DSN not supported for {engine.target_database_engine_name}"
            )
        return create_dsn_string(engine, **kwargs)
    
    # Handle standard connections
    return create_standard_connection_string(engine, **kwargs)
```

### 3. Configuration Template Usage
```python
def get_engine_configuration(engine: TargetDatabaseEngine) -> Dict[str, Any]:
    """Access engine-specific configuration"""
    config = engine.load_engine_config()
    
    return {
        'engine_name': engine.target_database_engine_name,
        'requires_auth': engine.requires_authentication,
        'supports_dsn': engine.supports_dsn,
        'placeholder': engine.get_placeholder(),
        'module': engine.import_module,
        'admin_handler': engine.get_admin_handler().__class__.__name__
    }
```

<a name="testing"></a>
## 🧪 Testing

### Unit Testing Examples
```python
def test_engine_validation():
    """Test engine validation functionality"""
    # Engine initialization
    engine = TargetDatabaseEngine.MYSQL
    assert engine.target_database_engine_name == "MYSQL"
    
    # Authentication requirement
    assert engine.requires_authentication is True
    
    # DSN support
    assert engine.supports_dsn is False
    
    # Connection option validation
    option = TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
    assert engine.validate_connection_option(option) is True
    
    dsn_option = TargetDatabaseConnectionStringOption.Default_DSN_AndDefaultUserPwd
    assert engine.validate_connection_option(dsn_option) is False
```

<a name="error-handling"></a>
## ⚠️ Error Handling

### Custom Exception Classes
```python
class DatabaseConnectionError(Exception):
    """Base exception for database connection errors."""
    pass

class InvalidConnectionOptionError(DatabaseConnectionError):
    """Raised when connection option is incompatible with database engine."""
    
    def __init__(self, engine: TargetDatabaseEngine, 
                 option: TargetDatabaseConnectionStringOption):
        self.engine = engine
        self.option = option
        message = f"Connection option {option.name} is not compatible with {engine.name}"
        super().__init__(message)
```

### Error Handling Implementation
```python
def connect_to_database(
    engine: TargetDatabaseEngine,
    option: TargetDatabaseConnectionStringOption,
    **kwargs
) -> Any:
    """Comprehensive connection handling with error management"""
    try:
        # Validate compatibility
        if not option.validate_for_engine(engine):
            raise InvalidConnectionOptionError(engine, option)
            
        # Load engine module
        module_name = engine.import_module
        if not module_name:
            raise DatabaseConnectionError(
                f"No module configured for {engine.target_database_engine_name}"
            )
            
        # Create connection
        conn_str = create_connection_string(engine, option, **kwargs)
        db_module = importlib.import_module(module_name)
        return db_module.connect(conn_str)
        
    except ImportError as e:
        raise DatabaseConnectionError(
            f"Failed to import {engine.target_database_engine_name} module: {str(e)}"
        )
    except Exception as e:
        raise DatabaseConnectionError(
            f"Connection failed for {engine.target_database_engine_name}: {str(e)}"
        )
```

---
📝 **Note**: This documentation assumes familiarity with Python enums and database connections. For basic concepts, please refer to the Python documentation.

🔗 **Related Resources**:
- [Python Enum Documentation](https://docs.python.org/3/library/enum.html)
- [Database API Specification v2.0](https://www.python.org/dev/peps/pep-0249/)