from typing import TypedDict, Optional, Dict, Any, Protocol, Union
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class ConnectionMode(Enum):
    """Connection mode enumeration"""
    DIRECT = "direct"
    DSN = "dsn"

class DatabaseType(Enum):
    """Supported database types"""
    MSSQL = "MSSQL"
    POSTGRESQL = "POSTGRESQL"
    MYSQL = "MYSQL"
    SQLITE = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

class Credentials(TypedDict):
    """Type definition for database credentials"""
    username: str
    password: str
    is_default: bool

class ConnectionParameters(TypedDict):
    """Type definition for connection parameters"""
    driver: Optional[str]
    dsn_name: Optional[str]
    database_name: str
    server: Optional[str]
    port_number: Optional[int]
    username: Optional[str]
    password: Optional[str]
    additional_params: Dict[str, Any]

@dataclass
class ConnectionConfig:
    """Configuration for database connection"""
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    driver: Optional[str] = None
    dsn: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    additional_params: Dict[str, Any] = None

    def merge(self, other: Dict[str, Any]) -> 'ConnectionConfig':
        """Merge additional parameters into configuration"""
        return ConnectionConfig(
            host=other.get('host', self.host),
            port=other.get('port', self.port),
            database=other.get('database', self.database),
            driver=other.get('driver', self.driver),
            dsn=other.get('dsn', self.dsn),
            username=other.get('username', self.username),
            password=other.get('password', self.password),
            additional_params={
                **(self.additional_params or {}),
                **other.get('additional_params', {})
            }
        )

class ConnectionStringBuilder(Protocol):
    """Protocol for building connection strings"""
    def build(
        self, 
        config: ConnectionConfig, 
        credentials: Optional[Credentials] = None
    ) -> str:
        """Build connection string from configuration and credentials"""
        ...

class ConnectionValidator(Protocol):
    """Protocol for validating connection parameters"""
    def validate_config(self, config: ConnectionConfig) -> bool:
        """Validate connection configuration"""
        ...
    
    def validate_credentials(self, credentials: Credentials) -> bool:
        """Validate credentials"""
        ...

@dataclass
class DatabaseTemplate:
    """Template for database engine configuration"""
    name: str
    module_name: str
    requires_auth: bool
    supports_dsn: bool
    parameter_placeholder: str
    default_config: ConnectionConfig
    connection_format: Dict[str, str]

@dataclass
class TemplateConfig:
    """Configuration for database template"""
    default_parameters: Dict[str, Any]
    format_connection_string: Dict[str, Any]
    crudbasic: Dict[str, Any]

class DatabaseError(Exception):
    """Base class for database errors"""
    pass

class ConnectionError(DatabaseError):
    """Error during database connection"""
    pass

class ValidationError(DatabaseError):
    """Error during parameter validation"""
    pass

@dataclass
class ConnectionResult:
    """Result of connection attempt"""
    success: bool
    connection: Optional[Any] = None
    error: Optional[str] = None

class ConnectionPool:
    """Configuration for connection pooling"""
    min_size: int
    max_size: int
    timeout: int
    max_overflow: int

@dataclass
class RetryConfig:
    """Configuration for connection retry attempts"""
    max_attempts: int
    delay: float
    backoff: float
    exceptions: tuple

@dataclass
class ConnectionMetrics:
    """Metrics for database connection"""
    connected_time: float
    last_used: float
    query_count: int
    error_count: int

class FileConnectionConfig(TypedDict):
    """Configuration for file-based databases"""
    path: Union[str, Path]
    filename: str
    create_if_missing: bool

class SSLConfig(TypedDict):
    """Configuration for SSL connections"""
    enabled: bool
    verify_cert: bool
    ca_cert: Optional[str]
    client_cert: Optional[str]
    client_key: Optional[str]

@dataclass
class TimeoutConfig:
    """Configuration for various timeouts"""
    connect: int = 30
    read: int = 30
    write: int = 30
    pool_timeout: int = 30
    command_timeout: int = 30

@dataclass
class ConnectionInfo:
    """Information about current connection"""
    database_type: DatabaseType
    mode: ConnectionMode
    config: ConnectionConfig
    connected: bool
    in_transaction: bool
    metrics: ConnectionMetrics

class EngineFeatures(TypedDict):
    """Features supported by database engine"""
    transactions: bool
    batch_operations: bool
    prepared_statements: bool
    connection_pooling: bool
    ssl_support: bool

@dataclass
class QueryParameters:
    """Parameters for database queries"""
    query: str
    params: Optional[tuple] = None
    timeout: Optional[int] = None
    fetch_size: Optional[int] = None
