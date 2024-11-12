# Database Connection Constants Documentation 🔌

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Engine Configuration](#engine-configuration)
3. [Usage Examples](#usage-examples)
4. [Advanced Patterns](#advanced-patterns)
5. [Error Handling](#error-handling)
6. [Connection Lifecycle](#connection-lifecycle)

## Core Concepts

Key Features:
- 🔑 Template-based configuration
- 🛡️ Built-in validation
- 🔄 Connection lifecycle management
- 🎯 Type safety
- 📦 Modular design

[Table of Contents](#Table-of-Contents)


### Engine Configuration Template
```python
ENGINE_CONFIG = {
    "DEFAULT_PARAMETERS": {
        # Connection basics 🔗
        "DRIVER": str,
        "CONNECTION_TEMPLATE": str,
        "DSN_TEMPLATE": Optional[str],
        
        # Parameters 📝
        "REQUIRED_PARAMS": List[str],
        "OPTIONAL_PARAMS": List[str]
    },
    "FEATURES": {
        "SUPPORTS_DSN": bool,
        "REQUIRES_AUTH": bool,
        "SUPPORTS_POOL": bool,
        "SUPPORTS_SSL": bool,
        "SUPPORTS_COMPRESSION": bool
    },
    "RUNTIME": {
        "MODULE": str,
        "PLACEHOLDER": str,
        "CREATE_CONNECTION": Callable,
        "VALIDATE_CONNECTION": Callable,
        "HEALTH_CHECK": Callable
    }
}
```
[Table of Contents](#Table-of-Contents)

## Engine Configuration

### PostgreSQL Configuration
```python
POSTGRESQL = {
    "DEFAULT_PARAMETERS": {
        "DRIVER": "{PostgreSQL ANSI}",
        "CONNECTION_TEMPLATE": "host={host} port={port} dbname={database} user={username} password={password}",
        "DSN_TEMPLATE": "DSN={dsn}",
        "REQUIRED_PARAMS": ["host", "database"],
        "OPTIONAL_PARAMS": ["port", "schema", "application_name"]
    },
    "FEATURES": {
        "SUPPORTS_DSN": True,
        "REQUIRES_AUTH": True,
        "SUPPORTS_POOL": True,
        "SUPPORTS_SSL": True,
        "SUPPORTS_COMPRESSION": True
    },
    "RUNTIME": {
        "MODULE": "psycopg2",
        "PLACEHOLDER": "%s",
        "CREATE_CONNECTION": lambda conn_str: psycopg2.connect(conn_str),
        "VALIDATE_CONNECTION": lambda conn: conn.status == psycopg2.extensions.STATUS_READY,
        "HEALTH_CHECK": lambda conn: conn.execute("SELECT 1")
    }
}
```

### MySQL Configuration
```python
MYSQL = {
    "DEFAULT_PARAMETERS": {
        "DRIVER": "{MySQL ODBC 8.0 Driver}",
        "CONNECTION_TEMPLATE": "DRIVER={driver};SERVER={host};PORT={port};DATABASE={database};UID={username};PWD={password}",
        "REQUIRED_PARAMS": ["host", "database", "username", "password"],
        "OPTIONAL_PARAMS": ["charset", "ssl_ca"]
    },
    "FEATURES": {
        "SUPPORTS_DSN": True,
        "REQUIRES_AUTH": True,
        "SUPPORTS_POOL": True,
        "SUPPORTS_SSL": True,
        "SUPPORTS_COMPRESSION": True
    },
    "RUNTIME": {
        "MODULE": "mysql.connector",
        "PLACEHOLDER": "%s",
        "CREATE_CONNECTION": lambda conn_str: mysql.connector.connect(**parse_conn_str(conn_str)),
        "VALIDATE_CONNECTION": lambda conn: conn.is_connected(),
        "HEALTH_CHECK": lambda conn: conn.ping(reconnect=True)
    }
}
```

### SQLite Configuration
```python
SQLITE = {
    "DEFAULT_PARAMETERS": {
        "DRIVER": "sqlite3",
        "CONNECTION_TEMPLATE": "{database}",
        "REQUIRED_PARAMS": ["database"],
        "OPTIONAL_PARAMS": ["timeout", "isolation_level"]
    },
    "FEATURES": {
        "SUPPORTS_DSN": False,
        "REQUIRES_AUTH": False,
        "SUPPORTS_POOL": False,
        "SUPPORTS_SSL": False,
        "SUPPORTS_COMPRESSION": False
    },
    "RUNTIME": {
        "MODULE": "sqlite3",
        "PLACEHOLDER": "?",
        "CREATE_CONNECTION": lambda conn_str: sqlite3.connect(conn_str),
        "VALIDATE_CONNECTION": lambda conn: True,
        "HEALTH_CHECK": lambda conn: conn.execute("SELECT 1")
    }
}
```

## Extended Validation Patterns

### Parameter Validation
```python
class ConnectionValidator:
    """Comprehensive connection parameter validation."""
    
    @staticmethod
    def validate_params(engine: TargetDatabaseEngine, 
                       params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize connection parameters."""
        config = get_engine_config(engine)
        
        # Required parameters
        missing = [
            param for param in config["DEFAULT_PARAMETERS"]["REQUIRED_PARAMS"]
            if param not in params
        ]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
        
        # Type validation
        type_validators = {
            "port": lambda x: isinstance(x, int) and 0 < x < 65536,
            "host": lambda x: isinstance(x, str) and len(x) > 0,
            "database": lambda x: isinstance(x, str) and len(x) > 0
        }
        
        for param, value in params.items():
            if param in type_validators and not type_validators[param](value):
                raise ValueError(f"Invalid value for {param}: {value}")
        
        return params

    @staticmethod
    def validate_ssl_params(params: Dict[str, Any]) -> None:
        """Validate SSL configuration parameters."""
        if params.get("ssl_mode") == "verify-full":
            required_ssl = ["ssl_ca", "ssl_cert", "ssl_key"]
            missing_ssl = [
                param for param in required_ssl
                if param not in params
            ]
            if missing_ssl:
                raise ValueError(f"SSL verification requires: {missing_ssl}")
```

## Error Handling Examples

```python
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Connection-related errors."""
    pass

class ValidationError(DatabaseError):
    """Parameter validation errors."""
    pass

class ConnectionManager:
    """Manage database connections with error handling."""
    
    def __init__(self, engine: TargetDatabaseEngine):
        self.engine = engine
        self.config = get_engine_config(engine)
        self.retries = 3
        self.retry_delay = 1  # seconds
        
    def connect_with_retry(self, params: Dict[str, Any]) -> Any:
        """Attempt connection with retries."""
        for attempt in range(self.retries):
            try:
                # Validate parameters
                validated_params = ConnectionValidator.validate_params(
                    self.engine, params
                )
                
                # Create connection
                conn = self.config["RUNTIME"]["CREATE_CONNECTION"](
                    self.build_conn_str(validated_params)
                )
                
                # Validate connection
                if not self.config["RUNTIME"]["VALIDATE_CONNECTION"](conn):
                    raise ConnectionError("Connection validation failed")
                
                return conn
                
            except Exception as e:
                if attempt == self.retries - 1:
                    raise ConnectionError(f"Failed to connect: {str(e)}")
                time.sleep(self.retry_delay * (attempt + 1))
```

## Connection Lifecycle Management

```python
class ConnectionLifecycle:
    """Manage database connection lifecycle."""
    
    def __init__(self, engine: TargetDatabaseEngine, params: Dict[str, Any]):
        self.manager = ConnectionManager(engine)
        self.params = params
        self.connection = None
        self.last_used = None
        self.health_check_interval = timedelta(minutes=5)
        
    @contextmanager
    def get_connection(self):
        """Get managed database connection."""
        try:
            if not self.connection:
                self.connection = self.manager.connect_with_retry(self.params)
            elif self._needs_health_check():
                self._check_connection_health()
                
            self.last_used = datetime.now()
            yield self.connection
            
        except Exception as e:
            self._handle_connection_error(e)
            raise
            
    def _needs_health_check(self) -> bool:
        """Determine if health check is needed."""
        return (
            self.last_used and 
            datetime.now() - self.last_used > self.health_check_interval
        )
    
    def _check_connection_health(self) -> None:
        """Check connection health and reconnect if needed."""
        try:
            self.manager.config["RUNTIME"]["HEALTH_CHECK"](self.connection)
        except Exception:
            self.connection = self.manager.connect_with_retry(self.params)
    
    def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection errors."""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            finally:
                self.connection = None
                self.last_used = None

# Usage Example
lifecycle = ConnectionLifecycle(
    TargetDatabaseEngine.POSTGRESQL,
    {
        "host": "localhost",
        "database": "myapp",
        "username": "user",
        "password": "pass"
    }
)

with lifecycle.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
```
