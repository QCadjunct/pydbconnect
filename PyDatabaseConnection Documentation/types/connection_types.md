# Database Connection Types Documentation

## Core Types and Classes

### 1. Enumerations

#### ConnectionMode
```python
class ConnectionMode(Enum):
    DIRECT = "direct"  # Direct database connection
    DSN = "dsn"       # Connection via Data Source Name
```

#### DatabaseType
```python
class DatabaseType(Enum):
    MSSQL = "MSSQL"
    POSTGRESQL = "POSTGRESQL"
    MYSQL = "MYSQL"
    SQLITE = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"
```

### 2. Type Definitions

#### Credentials
```python
class Credentials(TypedDict):
    username: str       # Database username
    password: str       # Database password
    is_default: bool    # Whether these are default credentials
```

#### ConnectionParameters
```python
class ConnectionParameters(TypedDict):
    driver: Optional[str]           # Database driver name
    dsn_name: Optional[str]         # DSN name if using DSN
    database_name: str              # Database name
    server: Optional[str]           # Server hostname
    port_number: Optional[int]      # Port number
    username: Optional[str]         # Username
    password: Optional[str]         # Password
    additional_params: Dict[str, Any] # Additional connection parameters
```

### 3. Configuration Classes

#### ConnectionConfig
```python
@dataclass
class ConnectionConfig:
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    driver: Optional[str] = None
    dsn: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    additional_params: Dict[str, Any] = None

    def merge(self, other: Dict[str, Any]) -> 'ConnectionConfig':
        """Merge additional parameters into existing configuration"""
```

#### DatabaseTemplate
```python
@dataclass
class DatabaseTemplate:
    name: str                    # Template name
    module_name: str             # Python module name
    requires_auth: bool          # Whether authentication is required
    supports_dsn: bool           # Whether DSN is supported
    parameter_placeholder: str   # SQL parameter placeholder
    default_config: ConnectionConfig  # Default configuration
    connection_format: Dict[str, str] # Connection string formats
```

### 4. Protocols

#### ConnectionStringBuilder
```python
class ConnectionStringBuilder(Protocol):
    def build(
        self, 
        config: ConnectionConfig, 
        credentials: Optional[Credentials] = None
    ) -> str:
        """Build connection string from configuration"""
```

#### ConnectionValidator
```python
class ConnectionValidator(Protocol):
    def validate_config(self, config: ConnectionConfig) -> bool:
        """Validate connection configuration"""
    
    def validate_credentials(self, credentials: Credentials) -> bool:
        """Validate credentials"""
```

### 5. Error Handling

```python
class DatabaseError(Exception):
    """Base class for database errors"""

class ConnectionError(DatabaseError):
    """Connection-specific errors"""

class ValidationError(DatabaseError):
    """Validation-specific errors"""
```

### 6. Connection Management

#### ConnectionPool
```python
class ConnectionPool:
    min_size: int      # Minimum pool size
    max_size: int      # Maximum pool size
    timeout: int       # Pool timeout
    max_overflow: int  # Maximum number of connections
```

#### RetryConfig
```python
@dataclass
class RetryConfig:
    max_attempts: int   # Maximum retry attempts
    delay: float       # Initial delay between retries
    backoff: float     # Backoff multiplier
    exceptions: tuple  # Retryable exceptions
```

### 7. Monitoring and Metrics

#### ConnectionMetrics
```python
@dataclass
class ConnectionMetrics:
    connected_time: float  # Time since connection established
    last_used: float      # Time since last used
    query_count: int      # Number of queries executed
    error_count: int      # Number of errors encountered
```

### 8. Security Configuration

#### SSLConfig
```python
class SSLConfig(TypedDict):
    enabled: bool
    verify_cert: bool
    ca_cert: Optional[str]
    client_cert: Optional[str]
    client_key: Optional[str]
```

### 9. Timeouts Configuration

#### TimeoutConfig
```python
@dataclass
class TimeoutConfig:
    connect: int = 30          # Connection timeout
    read: int = 30            # Read timeout
    write: int = 30           # Write timeout
    pool_timeout: int = 30    # Pool acquisition timeout
    command_timeout: int = 30  # Command execution timeout
```

## Usage Examples

### Basic Connection Configuration
```python
config = ConnectionConfig(
    host="localhost",
    port=5432,
    database="mydb",
    username="user",
    password="pass"
)

# With additional parameters
config = config.merge({
    'additional_params': {
        'application_name': 'myapp',
        'connect_timeout': 30
    }
})
```

### Template Configuration
```python
template = DatabaseTemplate(
    name="POSTGRESQL",
    module_name="psycopg2",
    requires_auth=True,
    supports_dsn=True,
    parameter_placeholder="%s",
    default_config=config,
    connection_format={
        "direct": "host={host} port={port} dbname={database}",
        "dsn": "dsn={dsn}"
    }
)
```

### SSL Configuration
```python
ssl_config = SSLConfig(
    enabled=True,
    verify_cert=True,
    ca_cert="/path/to/ca.crt",
    client_cert="/path/to/client.crt",
    client_key="/path/to/client.key"
)
```

### Retry Configuration
```python
retry_config = RetryConfig(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(ConnectionError, TimeoutError)
)
