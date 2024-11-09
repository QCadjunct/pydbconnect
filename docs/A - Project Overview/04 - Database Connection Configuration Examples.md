# Database Connection Configuration Examples

## 1. Template Configurations

### 1.1 MSSQL Configuration
 
MSSQL_CONFIG = {
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
                    "DRIVER={driver};"
                    "SERVER={server},{port};"
                    "DATABASE={database};"
                    "Trusted_Connection=no;"
                    "TrustServerCertificate=yes;"
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

# Environment Setup
MSSQL_ENV = {
    "MSSQL_USERNAME": "sa",
    "MSSQL_PASSWORD": "YourPassword",
    "MSSQL_DEFAULT_DATABASE": "master"
}
 

### 1.2 PostgreSQL Configuration
 
POSTGRESQL_CONFIG = {
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "postgres",
            "SERVER": "localhost",
            "PORT_NUMBER": 5432,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME", "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": (
                    "host={server} "
                    "port={port} "
                    "dbname={database} "
                    "application_name=pydatabaseconnection"
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

# Environment Setup
POSTGRESQL_ENV = {
    "POSTGRESQL_USERNAME": "postgres",
    "POSTGRESQL_PASSWORD": "YourPassword",
    "POSTGRESQL_DEFAULT_DATABASE": "postgres"
}
 

### 1.3 SQLite Configuration
 
SQLITE_CONFIG = {
    "SQLITE3": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "database.db",
            "FULLY_QUALIFIED_PATH": "path/to/database",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME", "FULLY_QUALIFIED_PATH"
                ],
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "{path}/{database}"
            }
        },
        "CRUDBASIC": {
            "IMPORT": "sqlite3",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False
        }
    }
}
 

## 2. Connection String Examples

### 2.1 Direct Connection Strings
 
# MSSQL Direct Connection
mssql_direct = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=Northwind;"
    "UID=sa;"
    "PWD=YourPassword;"
    "TrustServerCertificate=yes;"
)

# PostgreSQL Direct Connection
postgresql_direct = (
    "host=localhost "
    "port=5432 "
    "dbname=mydatabase "
    "user=postgres "
    "password=YourPassword "
    "application_name=myapp"
)

# MySQL Direct Connection
mysql_direct = (
    "DRIVER={MySQL ODBC 8.0 Driver};"
    "SERVER=localhost;"
    "PORT=3306;"
    "DATABASE=mydb;"
    "UID=root;"
    "PWD=YourPassword;"
    "CHARSET=utf8mb4;"
)
 

### 2.2 DSN Connection Strings
 
# MSSQL DSN
mssql_dsn = "DSN=MyMSSQLDSN;UID=sa;PWD=YourPassword;"

# PostgreSQL DSN
postgresql_dsn = "DSN=MyPostgreSQLDSN;UID=postgres;PWD=YourPassword;"

# MySQL DSN
mysql_dsn = "DSN=MyMySQLDSN;UID=root;PWD=YourPassword;"
 

## 3. Environment Configuration

### 3.1 .env File Template
 ini
# Database Credentials
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword
MSSQL_DEFAULT_DATABASE=master

POSTGRESQL_USERNAME=postgres
POSTGRESQL_PASSWORD=YourPassword
POSTGRESQL_DEFAULT_DATABASE=postgres

MYSQL_USERNAME=root
MYSQL_PASSWORD=YourPassword
MYSQL_DEFAULT_DATABASE=mysql

# Connection Settings
DEFAULT_CONNECTION_TIMEOUT=30
DEFAULT_COMMAND_TIMEOUT=60
DEFAULT_POOL_SIZE=5

# Debug Settings
DEBUG_MODE=False
LOG_LEVEL=INFO
 

### 3.2 Configuration Loading
 
from pathlib import Path
from dotenv import load_dotenv

def load_configuration():
    """Load configuration from environment and .env file"""
    env_path = Path('.') / '.env'
    load_dotenv(env_path)
    
    return {
        'credentials': {
            'mssql': {
                'username': os.getenv('MSSQL_USERNAME'),
                'password': os.getenv('MSSQL_PASSWORD'),
                'database': os.getenv('MSSQL_DEFAULT_DATABASE')
            },
            'postgresql': {
                'username': os.getenv('POSTGRESQL_USERNAME'),
                'password': os.getenv('POSTGRESQL_PASSWORD'),
                'database': os.getenv('POSTGRESQL_DEFAULT_DATABASE')
            }
        },
        'settings': {
            'timeout': int(os.getenv('DEFAULT_CONNECTION_TIMEOUT', 30)),
            'pool_size': int(os.getenv('DEFAULT_POOL_SIZE', 5)),
            'debug': os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        }
    }
 

## 4. Usage Examples

### 4.1 Basic Configuration Usage
 
# Direct connection with default configuration
db = DatabaseConnection("MSSQL") \
    .with_credentials_from_env() \
    .connect()

# Custom configuration
db = DatabaseConnection("POSTGRESQL") \
    .with_credentials("user", "pass") \
    .with_params(
        PORT_NUMBER=5433,
        DATABASE_NAME="custom_db"
    ) \
    .connect()

# DSN connection
db = DatabaseConnection("MYSQL", use_dsn=True) \
    .with_credentials_from_env() \
    .with_params(DSN_NAME="MyDSN") \
    .connect()
 

### 4.2 Advanced Configuration Usage
 
# Connection with timeout and pooling
from contextlib import contextmanager

@contextmanager
def get_db_connection(engine_type: str, **kwargs):### 6.2 Common Validation Errors

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
    db = DatabaseConnection(engine_type) \
        .with_credentials_from_env() \
        .with_params(**kwargs) \
        .connect()
    try:
        yield db
    finally:
        db.close()

# Usage
with get_db_connection(
    "MSSQL",
    CONNECTION_TIMEOUT=60,
    POOL_SIZE=10
) as db:
    results = db.query_to_dataframe("SELECT * FROM users")
 