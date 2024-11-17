# Database Engine Template Modules Documentation

## Table of Contents 📚 <a name="table-of-contents"></a>

1. [🏗️ Architecture Overview](#architecture-overview)
   - [🎯 Design Philosophy](#design-philosophy)
   - [🔧 Core Architecture Components](#core-architecture-components)
   - [⚙️ Configuration Structure](#configuration-structure)

2. [🧩 Core Components](#core-components)
   - [🛠️ Utility Functions](#utility-functions)
   - [🔗 Connection String Formatting](#connection-string-formatting)

3. [🔌 Database Engine Configurations](#database-engine-configurations)
   - [🖥️ Microsoft SQL Server (MSSQL)](#microsoft-sql-server)
   - [🐬 MySQL](#mysql)
   - [🐘 PostgreSQL](#postgresql)
   - [📦 SQLite3](#sqlite3)
   - [🦆 DuckDB](#duckdb)
   - [🔄 Psycopg2](#psycopg2)

4. [🎯 Usage Examples](#usage-examples)
   - [🔗 Basic Connection Patterns](#basic-connection-patterns)
   - [⚙️ Parameter Management](#parameter-management)
   - [📋 Complete Connection Examples](#complete-connection-examples)

5. [✨ Best Practices](#best-practices)
   - [🔄 Connection Management](#connection-management)
   - [🔒 Security Practices](#security-practices)
   - [⚡ Performance Optimization](#performance-optimization)

6. [❌ Error Handling](#error-handling)
   - [🌳 Exception Hierarchy](#exception-hierarchy)
   - [🎯 Error Handling Patterns](#error-handling-patterns)
   - [📝 Logging and Monitoring](#logging-and-monitoring)

7. [🔧 Troubleshooting Guide](#troubleshooting-guide)
   - [❗ Common Issues and Solutions](#common-issues-and-solutions)
   - [🔍 Diagnostic Tools](#diagnostic-tools)
   - [🛠️ Maintenance Procedures](#maintenance-procedures)

## 🏗️ Architecture Overview <a name="architecture-overview"></a>

### 🎯 Design Philosophy <a name="design-philosophy"></a>

The database engine template system is built on the following core principles:

1. Standardized Interface
   - Consistent configuration structure across all database engines
   - Unified connection parameter management
   - Standardized error handling patterns
   - Common transaction management approach

2. Security-First Design
   - Secure credential management
   - Parameter sanitization
   - Connection string safety
   - Encryption support where available

3. Modular Architecture
   - Independent engine configurations
   - Pluggable connection handlers
   - Extensible template system
   - Reusable components

4. Performance Optimization
   - Connection pooling support
   - Resource cleanup automation
   - Efficient parameter handling
   - Optimized string formatting

[🔝 Back to Table of Contents](#table-of-contents)

### 🔧 Core Architecture Components <a name="core-architecture-components"></a>

The system consists of the following key components:

1. Module Management
```python
def get_db_target_engine_module(module_name: str) -> Any:
    """
    Dynamically imports database modules.
    
    Args:
        module_name (str): Name of the module to import
        
    Returns:
        Imported module object
        
    Examples:
        pyodbc = get_db_target_engine_module('pyodbc')
        psycopg2 = get_db_target_engine_module('psycopg2')
        duckdb = get_db_target_engine_module('duckdb')
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}. Make sure it's installed.") from e
```

2. Parameter Management
```python
def load_default_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads non-credential default parameters.
    
    Args:
        target_database_engine (str): Database engine identifier
        d (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dictionary of filtered parameters excluding credentials
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
    return {key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
            for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]}
```

3. Connection String Management
```python
def load_dsn_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads DSN-specific parameters.
    
    Args:
        target_database_engine (str): Database engine identifier
        d (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dictionary of DSN parameters excluding credentials
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DSN_PARAMETER_KEYS"]
    return {key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
            for key in [k for k in keys if k not in ["UID", "PWD"]]}
```

[🔝 Back to Table of Contents](#table-of-contents)

### ⚙️ Configuration Structure <a name="configuration-structure"></a>

Each database engine template follows this standardized structure:

1. Default Parameters Section
```python
"DEFAULT_PARAMETERS": {
    "DRIVER": "driver_name",
    "DSN_NAME": "dsn_name",
    "DATABASE_NAME": "database_name",
    "SERVER": "server_name",
    "PORT_NUMBER": port_number,
    "USERNAME": "username",
    "PASSWORD": "password",
    "FORMAT_CONNECTION_STRING": {
        "LOAD_DEFAULT_PARAMETER_KEYS": ["key1", "key2"],
        "LOAD_DSN_PARAMETER_KEYS": ["dsn_key1", "dsn_key2"],
        "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
        "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
        "IS_DSN_NAME_SUPPORTED": True/False,
        "BASE_CONNECTION_STRING": "connection_string_template",
        "BASE_ODBC_DSN_CONNECTION_STRING": "dsn_string_template"
    }
}
```

2. Connection Parameters Section
```python
"FINALIZED_CONNECTION_PARAMS": {
    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: connection_string_formatter,
    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: dsn_string_formatter
}
```

3. Basic Operations Configuration
```python
"CRUDBASIC": {
    "IMPORT": "module_name",
    "PARAMETER_PLACEHOLDER": "placeholder_character",
    "IS_USERNAME_AND_PASSWORD_REQUIRED": True/False
}
```

4. Connection Creation Configuration
```python
"CREATE_DATABASE_CONNECTION": {
    "CONNECTION_NOTES": "usage_notes",
    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda conn_string: connection_creator
}
```

[🔝 Back to Table of Contents](#table-of-contents)

## 🧩 Core Components <a name="core-components"></a>

### 🛠️ Utility Functions <a name="utility-functions"></a>

#### Module Loading System
```python
from typing import Any, Dict
import importlib

def get_db_target_engine_module(module_name: str) -> Any:
    """
    Dynamically imports database modules.
    
    Args:
        module_name (str): Name of the module to import
        
    Returns:
        Imported module object
        
    Raises:
        ImportError: If module import fails
        
    Example:
        # Load MSSQL driver
        mssql_module = get_db_target_engine_module('pyodbc')
        
        # Load PostgreSQL driver
        pg_module = get_db_target_engine_module('psycopg2')
        
        # Load DuckDB driver
        duck_module = get_db_target_engine_module('duckdb')
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}. Make sure it's installed.") from e

```

#### Parameter Management System
```python
def load_default_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads non-credential default parameters.
    
    Args:
        target_database_engine (str): Database engine identifier
        d (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dictionary of filtered parameters excluding credentials
        
    Example:
        # Load MSSQL parameters
        mssql_params = load_default_parameter_keys_dict('MSSQL', config_dict)
        print(mssql_params)
        # Output:
        # {
        #     'DRIVER': '{ODBC Driver 17 for SQL Server}',
        #     'DSN_NAME': 'Northwinds2024StudentDSN',
        #     'DATABASE_NAME': 'Northwinds2024Student',
        #     'SERVER': 'localhost',
        #     'PORT_NUMBER': 13001
        # }
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
    return {key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
            for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]}

def load_dsn_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads DSN-specific parameters.
    
    Args:
        target_database_engine (str): Database engine identifier
        d (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dictionary of DSN parameters excluding credentials
        
    Example:
        # Load MSSQL DSN parameters
        mssql_dsn_params = load_dsn_parameter_keys_dict('MSSQL', config_dict)
        print(mssql_dsn_params)
        # Output:
        # {
        #     'DSN': 'Northwinds2024StudentDSN'
        # }
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DSN_PARAMETER_KEYS"]
    return {key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
            for key in [k for k in keys if k not in ["UID", "PWD"]]}
```

[🔝 Back to Table of Contents](#table-of-contents)

### 🔗 Connection String Formatting <a name="connection-string-formatting"></a>

#### Base Connection String Templates

1. MSSQL Connection Strings
```python
# Direct Connection Template
MSSQL_BASE_STRING = "DRIVER={0}; SERVER={1},{2}; DATABASE={3}; UID={4}; PWD={5};"
# Example: "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=localhost,1433; DATABASE=Northwind; UID=sa; PWD=password;"

# DSN Connection Template
MSSQL_DSN_STRING = "DSN={0};UID={1};PWD={2};"
# Example: "DSN=NorthwindDSN;UID=sa;PWD=password;"
```

2. MySQL Connection Strings
```python
# Direct Connection Template
MYSQL_BASE_STRING = "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5}; MULTI_HOST=1; CHARSET={6};"
# Example: "DRIVER={MySQL ODBC 8.2 ANSI Driver}; SERVER=localhost; PORT=3306; DATABASE=Northwind; UID=root; PWD=password; MULTI_HOST=1; CHARSET=utf8mb4;"

# DSN Connection Template
MYSQL_DSN_STRING = "DSN={0};UID={1};PWD={2};"
# Example: "DSN=MySQLNorthwindDSN;UID=root;PWD=password;"
```

3. PostgreSQL Connection Strings
```python
# Direct Connection Template
POSTGRESQL_BASE_STRING = "DRIVER={0}; SERVER={1}; Port={2}; DATABASE={3}; UID={4}; PWD={5};"
# Example: "DRIVER={PostgreSQL ANSI(x64)}; SERVER=localhost; Port=5432; DATABASE=Northwind; UID=postgres; PWD=password;"

# DSN Connection Template
POSTGRESQL_DSN_STRING = "DSN={0};UID={1};PWD={2};"
# Example: "DSN=PostgreSQLDSN;UID=postgres;PWD=password;"
```

4. SQLite3 Connection Strings
```python
# Direct Connection Template
SQLITE3_BASE_STRING = "Driver={0};Database={1}{2};LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;"
# Example: "Driver={SQLite3 ODBC Driver};Database=D:\Sqlite3\Databases\chinook.db;LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;"

# DSN Connection Template
SQLITE3_DSN_STRING = "DSN={0};"
# Example: "DSN=ChinookDatabaseDSN;"
```

5. DuckDB Connection Strings
```python
# Direct Connection Template
DUCKDB_BASE_STRING = "{0}\\{1}"
# Example: "Q:\Database\Accounting\Accounting.duckdb"

# No DSN support for DuckDB
```

6. Psycopg2 Connection Strings
```python
# Direct Connection Template
PSYCOPG2_BASE_STRING = "host={0} port={1} dbname={2} user={3} password={4}"
# Example: "host=localhost port=5432 dbname=Northwind user=postgres password=password"

# No DSN support for Psycopg2
```

#### Connection String Formatting Functions

```python
def format_connection_string(engine_type: str, params: Dict[str, Any], use_dsn: bool = False) -> str:
    """
    Formats connection string based on engine type and parameters.
    
    Args:
        engine_type: Database engine identifier
        params: Connection parameters
        use_dsn: Whether to use DSN connection string
        
    Returns:
        Formatted connection string
        
    Example:
        params = {
            'SERVER': 'localhost',
            'PORT_NUMBER': 1433,
            'DATABASE_NAME': 'Northwind',
            'USERNAME': 'sa',
            'PASSWORD': 'password'
        }
        conn_str = format_connection_string('MSSQL', params)
        print(conn_str)
        # Output: "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=localhost,1433; DATABASE=Northwind; UID=sa; PWD=password;"
    """
    template = get_connection_string_template(engine_type, use_dsn)
    return format_string_with_params(template, params)
```

[🔝 Back to Table of Contents](#table-of-contents)

## 🔌 Database Engine Configurations <a name="database-engine-configurations"></a>

### 🖥️ Microsoft SQL Server (MSSQL) <a name="microsoft-sql-server"></a>

#### Complete MSSQL Configuration
```python
MSSQL: Dict[str, Dict[str, Any]] = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "DSN_NAME": "Northwinds2024StudentDSN",
            "DATABASE_NAME": "Northwinds2024Student",
            "SERVER": "localhost",
            "PORT_NUMBER": 13001,
            "USERNAME": "sa",
            "PASSWORD": "PH@123456789",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME", "DATABASE_NAME", "SERVER", "PORT_NUMBER"],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1},{2}; DATABASE={3}; UID={4}; PWD={5};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["MSSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["MSSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            )
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}

# Usage Example
def create_mssql_connection():
    """
    Creates MSSQL connection using the template configuration.
    
    Returns:
        pyodbc.Connection: Active database connection
        
    Example:
        conn = create_mssql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
        conn.close()
    """
    config = MSSQL["MSSQL"]
    conn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MSSQL)
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_string)()
```

#### MSSQL Specific Features
1. Connection Methods
   - Direct TCP/IP connection
   - DSN-based connection
   - Named pipes
   - Shared memory

2. Authentication Modes
   - SQL Server authentication
   - Windows authentication
   - Azure Active Directory

3. TLS/SSL Configuration
   - Encryption enabled/disabled
   - Trust server certificate
   - Certificate validation

[🔝 Back to Table of Contents](#table-of-contents)

### 🐬 MySQL <a name="mysql"></a>

#### Complete MySQL Configuration
```python
MYSQL: Dict[str, Dict[str, Any]] = {
    "MYSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{MySQL ODBC 8.2 ANSI Driver}",
            "DSN_NAME": "MySQLNorthwindOrderDSN",
            "SERVER": "localhost",
            "PORT_NUMBER": 20101,
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "USERNAME": "root",
            "PASSWORD": "Password",
            "MULTI_HOST": 1,
            "CHARSET": "utf8mb4",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME", "DATABASE_NAME", "SERVER", "PORT_NUMBER", "MULTI_HOST"],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5}; MULTI_HOST=1; CHARSET={6};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["MYSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["CHARSET"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["MYSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            )
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}

# Usage Example
def create_mysql_connection():
    """
    Creates MySQL connection using the template configuration.
    
    Returns:
        pyodbc.Connection: Active database connection
        
    Example:
        conn = create_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
        conn.close()
    """
    config = MYSQL["MYSQL"]
    conn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MYSQL)
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_string)()
```

#### MySQL Specific Features
1. Character Sets and Collations
   - UTF-8 support
   - Multi-language support
   - Collation configuration

2. Multi-Host Support
   - Load balancing
   - Failover configuration
   - Replica selection

3. Security Features
   - SSL/TLS encryption
   - Authentication plugins
   - Connection compression

[🔝 Back to Table of Contents](#table-of-contents)

### 🐘 PostgreSQL <a name="postgresql"></a>

#### Complete PostgreSQL Configuration
```python
POSTGRESQL: Dict[str, Dict[str, Any]] = {
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{PostgreSQL ANSI(x64)}",
            "DSN_NAME": "PostgreSQL_DSN",
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME", "DATABASE_NAME", "SERVER", "PORT_NUMBER"],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; Port={2}; DATABASE={3}; UID={4}; PWD={5};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            )
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}

# Usage Example
def create_postgresql_connection():
    """
    Creates PostgreSQL connection using the template configuration.
    
    Returns:
        pyodbc.Connection: Active database connection
        
    Example:
        conn = create_postgresql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
        conn.close()
    """
    config = POSTGRESQL["POSTGRESQL"]
    conn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](POSTGRESQL)
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_string)()
```

#### PostgreSQL Specific Features
1. Schema Support
   - Multi-schema databases
   - Schema search paths
   - Schema permissions

2. SSL Modes
   - require
   - verify-ca
   - verify-full
   - prefer
   - disable

3. Connection Pooling
   - Maximum connections
   - Idle timeout
   - Connection lifecycle

[🔝 Back to Table of Contents](#table-of-contents)

### 📦 SQLite3 <a name="sqlite3"></a>

#### Complete SQLite3 Configuration
```python
SQLITE3: Dict[str, Dict[str, Any]] = {
    "SQLITE3": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{SQLite3 ODBC Driver}",
            "DSN_NAME": "ChinookDatabaseDSN",
            "FULLY_QUALIFIED_PATH": r"D:\\Sqlite3\\Databases",
            "DATABASE_NAME": r"chinook.db",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME", "FULLY_QUALIFIED_PATH", "DATABASE_NAME"],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "Driver={0};Database={1}{2};LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};"
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["SQLITE3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"],
                "\\" + d["SQLITE3"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["SQLITE3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            )
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}

# Usage Example
def create_sqlite3_connection():
    """
    Creates SQLite3 connection using the template configuration.
    
    Returns:
        pyodbc.Connection: Active database connection
        
    Example:
        conn = create_sqlite3_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
        conn.close()
    """
    config = SQLITE3["SQLITE3"]
    conn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](SQLITE3)
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_string)()
```

#### SQLite3 Specific Features
1. Journal Modes
   - DELETE
   - TRUNCATE
   - PERSIST
   - MEMORY
   - WAL
   - OFF

2. Synchronization Settings
   - FULL
   - NORMAL
   - OFF

3. Locking Modes
   - NORMAL
   - EXCLUSIVE

[🔝 Back to Table of Contents](#table-of-contents)

### 🦆 DuckDB <a name="duckdb"></a>

#### Complete DuckDB Configuration
```python
DUCKDB: Dict[str, Dict[str, Any]] = {
    "DUCKDB": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{DuckDB Driver}",
            "DSN_NAME": "",
            "FULLY_QUALIFIED_PATH": r"Q:\\Database\\Accounting",
            "DATABASE_NAME": r"Accounting.duckdb",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME", "FULLY_QUALIFIED_PATH", "DATABASE_NAME"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "{0}\\{1}",
                "BASE_ODBC_DSN_CONNECTION_STRING": None
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["DUCKDB"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["DUCKDB"]["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"],
                d["DUCKDB"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: None
        },
        "CRUDBASIC": {
            "IMPORT": "duckdb",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use duckdb.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('duckdb').connect(finalized_parameter_connection_string)
        }
    }
}

# Usage Example
def create_duckdb_connection(in_memory: bool = False):
    """
    Creates DuckDB connection using the template configuration.
    
    Args:
        in_memory (bool): Whether to create an in-memory database
    
    Returns:
        duckdb.DuckDBPyConnection: Active database connection
        
    Example:
        # File-based connection
        conn = create_duckdb_connection()
        result = conn.execute("SELECT COUNT(*) FROM information_schema.tables").fetchone()[0]
        conn.close()
        
        # In-memory connection
        mem_conn = create_duckdb_connection(in_memory=True)
        mem_conn.execute("CREATE TABLE test (id INTEGER, name VARCHAR)")
        mem_conn.close()
    """
    if in_memory:
        return get_db_target_engine_module('duckdb').connect(':memory:')
    
    config = DUCKDB["DUCKDB"]
    conn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](DUCKDB)
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_string)()
```

#### DuckDB Specific Features
1. Memory Management
   - In-memory databases
   - Memory limits
   - Memory buffering

2. File Access
   - Read-only mode
   - File locking
   - Temporary files

3. Extension Management
   - Loading extensions
   - Custom functions
   - User-defined types

[🔝 Back to Table of Contents](#table-of-contents)

### 🔄 Psycopg2 <a name="psycopg2"></a>

#### Complete Psycopg2 Configuration
```python
PSYCOPG2: Dict[str, Dict[str, Any]] = {
    "PSYCOPG2": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DATABASE_NAME", "SERVER", "PORT_NUMBER"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "host={0} port={1} dbname={2} user={3} password={4}",
                "BASE_ODBC_DSN_CONNECTION_STRING": None
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: None
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg2",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use psycopg2.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('psycopg2').connect(finalized_parameter_connection_string)
        }
    }
}

# Usage Example
def create_psycopg2_connection(application_name: str = None):
    """
    Creates Psycopg2 connection using the template configuration.
    
    Args:
        application_name (str, optional): Name of the application for monitoring
    
    Returns:
        psycopg2.connection: Active database connection
        
    Example:
        # Basic connection
        conn = create_psycopg2_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
        conn.close()
        
        # Connection with application name
        app_conn = create_psycopg2_connection("MyAnalyticsApp")
        with app_conn.cursor() as cur:
            cur.execute("SELECT current_setting('application_name')")
            app_name = cur.fetchone()[0]
        app_conn.close()
    """
    config = PSYCOPG2["PSYCOPG2"]
    conn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG2)
    
    if application_name:
        conn_string += f" application_name={application_name}"
    
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_string)()
```

#### Psycopg2 Specific Features
1. Advanced Data Types
   - Array support
   - JSON/JSONB handling
   - Composite types
   - Custom type adapters

2. Asynchronous Operations
   - Async connections
   - Async cursors
   - Notification handling

3. Transaction Management
   - Isolation levels
   - Savepoints
   - Two-phase commit

4. Security Features
   - SSL/TLS support
   - Connection encryption
   - Certificate validation
   - Password encryption

[🔝 Back to Table of Contents](#table-of-contents)

## 🎯 Usage Examples <a name="usage-examples"></a>

### 🔗 Basic Connection Patterns <a name="basic-connection-patterns"></a>

#### 1. Standard Connection Pattern
```python
def basic_connection_example():
    """Demonstrates standard connection pattern for all database engines."""
    
    # MSSQL Connection
    def mssql_example():
        config = MSSQL["MSSQL"]
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MSSQL)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                print(f"MSSQL Version: {version}")
    
    # MySQL Connection
    def mysql_example():
        config = MYSQL["MYSQL"]
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MYSQL)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"MySQL Version: {version}")
    
    # PostgreSQL Connection
    def postgresql_example():
        config = POSTGRESQL["POSTGRESQL"]
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](POSTGRESQL)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"PostgreSQL Version: {version}")

    # Execute examples with proper error handling
    for example in [mssql_example, mysql_example, postgresql_example]:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {str(e)}")
```

#### 2. DSN Connection Pattern
```python
def dsn_connection_example():
    """Demonstrates DSN connection pattern for supported databases."""
    
    # MSSQL DSN Connection
    def mssql_dsn_example():
        config = MSSQL["MSSQL"]
        dsn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](MSSQL)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](dsn_string)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DB_NAME()")
                database = cursor.fetchone()[0]
                print(f"Connected to MSSQL database: {database}")
    
    # MySQL DSN Connection
    def mysql_dsn_example():
        config = MYSQL["MYSQL"]
        dsn_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](MYSQL)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](dsn_string)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DATABASE()")
                database = cursor.fetchone()[0]
                print(f"Connected to MySQL database: {database}")

    # Execute DSN examples
    for example in [mssql_dsn_example, mysql_dsn_example]:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {str(e)}")
```

#### 3. File-Based Connection Pattern
```python
def file_based_connection_example():
    """Demonstrates connection pattern for file-based databases."""
    
    # SQLite3 Connection
    def sqlite3_example():
        config = SQLITE3["SQLITE3"]
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](SQLITE3)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                print(f"SQLite3 Version: {version}")
    
    # DuckDB Connection
    def duckdb_example():
        config = DUCKDB["DUCKDB"]
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](DUCKDB)
        with config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)() as conn:
            result = conn.execute("SELECT version()").fetchone()[0]
            print(f"DuckDB Version: {result}")

    # Execute file-based examples
    for example in [sqlite3_example, duckdb_example]:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {str(e)}")
```

### ⚙️ Parameter Management <a name="parameter-management"></a>

#### 1. Custom Parameter Configuration
```python
def custom_parameter_example():
    """Demonstrates custom parameter configuration for different databases."""
    
    # MSSQL Custom Parameters
    def mssql_custom_params():
        custom_params = {
            "SERVER": "custom-server",
            "PORT_NUMBER": 1433,
            "DATABASE_NAME": "CustomDB",
            "APPLICATION_NAME": "CustomApp",
            "CONNECT_TIMEOUT": 30,
            "ENCRYPT": "yes",
            "TRUST_SERVER_CERTIFICATE": "no"
        }
        
        config = MSSQL["MSSQL"]
        base_params = load_default_parameter_keys_dict("MSSQL", MSSQL)
        base_params.update(custom_params)
        
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](
            {"MSSQL": {"DEFAULT_PARAMETERS": base_params}}
        )
        return connection_string
    
    # PostgreSQL Custom Parameters
    def postgresql_custom_params():
        custom_params = {
            "SERVER": "custom-server",
            "PORT_NUMBER": 5432,
            "DATABASE_NAME": "CustomDB",
            "APPLICATION_NAME": "CustomApp",
            "SSL_MODE": "verify-full",
            "TARGET_SESSION_ATTRS": "read-write",
            "KEEPALIVES": 1,
            "KEEPALIVES_IDLE": 60
        }
        
        config = POSTGRESQL["POSTGRESQL"]
        base_params = load_default_parameter_keys_dict("POSTGRESQL", POSTGRESQL)
        base_params.update(custom_params)
        
        connection_string = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](
            {"POSTGRESQL": {"DEFAULT_PARAMETERS": base_params}}
        )
        return connection_string

    # Print formatted connection strings
    print("MSSQL Custom Connection String:", mssql_custom_params())
    print("PostgreSQL Custom Connection String:", postgresql_custom_params())
```

[🔝 Back to Table of Contents](#table-of-contents)

### 📋 Complete Connection Examples <a name="complete-connection-examples"></a>

#### 1. Production-Ready MSSQL Implementation
```python
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

class MSSQLDatabaseManager:
    """Production-ready MSSQL database manager implementation."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = MSSQL["MSSQL"]
        if config_override:
            self._apply_config_override(config_override)
        
    def _apply_config_override(self, override: Dict[str, Any]) -> None:
        """Applies configuration overrides with validation."""
        for key, value in override.items():
            if key in self.config["DEFAULT_PARAMETERS"]:
                self.config["DEFAULT_PARAMETERS"][key] = value
            else:
                self.logger.warning(f"Ignoring unknown configuration parameter: {key}")

    @contextmanager
    def get_connection(self, auto_commit: bool = False):
        """
        Gets a database connection with proper error handling and cleanup.
        
        Args:
            auto_commit (bool): Whether to enable automatic transaction commit
            
        Yields:
            pyodbc.Connection: Active database connection
            
        Example:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT TOP 1 * FROM Users")
                    user = cursor.fetchone()
        """
        connection = None
        try:
            connection_string = self.config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MSSQL)
            connection = self.config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)()
            
            if auto_commit:
                connection.autocommit = True
            
            yield connection
            
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {str(e)}")

    @contextmanager
    def transaction(self):
        """
        Manages a database transaction with automatic rollback on error.
        
        Example:
            with db_manager.transaction() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO Users (Name) VALUES (?)", ["John"])
                    cursor.execute("UPDATE UserCount SET Count = Count + 1")
        """
        with self.get_connection() as connection:
            try:
                connection.autocommit = False
                yield connection
                connection.commit()
            except Exception as e:
                connection.rollback()
                self.logger.error(f"Transaction failed: {str(e)}")
                raise

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Executes a query and returns all results.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            
        Returns:
            list: Query results
            
        Example:
            results = db_manager.execute_query(
                "SELECT * FROM Users WHERE Department = ?",
                ("IT",)
            )
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return [dict(zip([column[0] for column in cursor.description], row))
                        for row in cursor.fetchall()]

    def execute_many(self, query: str, params_list: list) -> int:
        """
        Executes a query multiple times with different parameters.
        
        Args:
            query (str): SQL query to execute
            params_list (list): List of parameter tuples
            
        Returns:
            int: Number of affected rows
            
        Example:
            rows_affected = db_manager.execute_many(
                "INSERT INTO Users (Name, Department) VALUES (?, ?)",
                [("John", "IT"), ("Jane", "HR")]
            )
        """
        with self.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount

# Usage Example
def mssql_production_example():
    """Demonstrates production usage of the MSSQL database manager."""
    
    # Configuration
    config_override = {
        "SERVER": "prod-server",
        "DATABASE_NAME": "ProductionDB",
        "PORT_NUMBER": 1433,
        "APPLICATION_NAME": "ProductionApp"
    }
    
    # Initialize manager
    db_manager = MSSQLDatabaseManager(config_override)
    
    try:
        # Basic query execution
        users = db_manager.execute_query("SELECT TOP 5 * FROM Users")
        print("Users:", users)
        
        # Transaction example
        with db_manager.transaction() as conn:
            with conn.cursor() as cursor:
                # Insert new user
                cursor.execute("""
                    INSERT INTO Users (Name, Email, Department)
                    VALUES (?, ?, ?)
                """, ("John Doe", "john.doe@example.com", "IT"))
                
                # Update department count
                cursor.execute("""
                    UPDATE DepartmentStats
                    SET EmployeeCount = EmployeeCount + 1
                    WHERE Department = ?
                """, ("IT",))
        
        # Batch insert example
        new_users = [
            ("Jane Smith", "jane.smith@example.com", "HR"),
            ("Bob Johnson", "bob.johnson@example.com", "Finance")
        ]
        affected_rows = db_manager.execute_many("""
            INSERT INTO Users (Name, Email, Department)
            VALUES (?, ?, ?)
        """, new_users)
        print(f"Inserted {affected_rows} new users")
        
    except Exception as e:
        print(f"Error in production example: {str(e)}")
```

[🔝 Back to Table of Contents](#table-of-contents)

#### 2. Production-Ready PostgreSQL Implementation
```python
from typing import Optional, Dict, Any, List, Union
import logging
from contextlib import contextmanager
from datetime import datetime

class PostgreSQLDatabaseManager:
    """Production-ready PostgreSQL database manager implementation."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = POSTGRESQL["POSTGRESQL"]
        self.schema = "public"  # Default schema
        if config_override:
            self._apply_config_override(config_override)
            
    def _apply_config_override(self, override: Dict[str, Any]) -> None:
        """Applies configuration overrides with validation."""
        for key, value in override.items():
            if key == "SCHEMA":
                self.schema = value
            elif key in self.config["DEFAULT_PARAMETERS"]:
                self.config["DEFAULT_PARAMETERS"][key] = value
            else:
                self.logger.warning(f"Ignoring unknown configuration parameter: {key}")

    @contextmanager
    def get_connection(self, application_name: Optional[str] = None):
        """
        Gets a database connection with proper error handling and cleanup.
        
        Args:
            application_name (str, optional): Name to identify the application in pg_stat_activity
            
        Yields:
            psycopg2.connection: Active database connection
            
        Example:
            with db_manager.get_connection("MyApp") as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT current_schema()")
                    schema = cursor.fetchone()[0]
        """
        connection = None
        try:
            # Build connection string with additional parameters
            connection_string = self.config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](POSTGRESQL)
            if application_name:
                connection_string += f" application_name='{application_name}'"
            
            connection = self.config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)()
            
            # Set search path
            with connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {self.schema}")
            
            yield connection
            
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {str(e)}")

    @contextmanager
    def transaction(self, isolation_level: Optional[str] = None):
        """
        Manages a database transaction with specific isolation level.
        
        Args:
            isolation_level (str, optional): Transaction isolation level
                (READ COMMITTED, REPEATABLE READ, SERIALIZABLE)
                
        Example:
            with db_manager.transaction("SERIALIZABLE") as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO users (name) VALUES (%s)", ["John"])
        """
        with self.get_connection() as connection:
            try:
                if isolation_level:
                    with connection.cursor() as cursor:
                        cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                
                connection.autocommit = False
                yield connection
                connection.commit()
                
            except Exception as e:
                connection.rollback()
                self.logger.error(f"Transaction failed: {str(e)}")
                raise

    def execute_query(self, 
                     query: str, 
                     params: Optional[tuple] = None,
                     fetch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Executes a query with server-side cursor for large result sets.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            fetch_size (int, optional): Number of rows to fetch at a time
            
        Returns:
            list: Query results as dictionaries
            
        Example:
            results = db_manager.execute_query(
                "SELECT * FROM users WHERE department = %s",
                ("IT",),
                fetch_size=1000
            )
        """
        with self.get_connection() as conn:
            if fetch_size:
                # Use server-side cursor for large result sets
                with conn.cursor(name='fetch_large_results') as cursor:
                    cursor.arraysize = fetch_size
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    while True:
                        rows = cursor.fetchmany(fetch_size)
                        if not rows:
                            break
                        for row in rows:
                            yield dict(zip([desc[0] for desc in cursor.description], row))
            else:
                # Use client-side cursor for small result sets
                with conn.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return [dict(zip([desc[0] for desc in cursor.description], row))
                            for row in cursor.fetchall()]

    def execute_many(self, 
                    query: str, 
                    params_list: list,
                    page_size: int = 1000) -> int:
        """
        Executes a query multiple times with batched parameters.
        
        Args:
            query (str): SQL query to execute
            params_list (list): List of parameter tuples
            page_size (int): Number of operations per batch
            
        Returns:
            int: Total number of affected rows
            
        Example:
            rows_affected = db_manager.execute_many(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                [("John", "john@example.com"), ("Jane", "jane@example.com")],
                page_size=100
            )
        """
        total_affected = 0
        with self.transaction() as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(params_list), page_size):
                    batch = params_list[i:i + page_size]
                    cursor.executemany(query, batch)
                    total_affected += cursor.rowcount
                    
                return total_affected

    def execute_copy(self, 
                    table_name: str, 
                    columns: List[str], 
                    data: List[tuple],
                    schema: Optional[str] = None) -> int:
        """
        Efficiently copies data using PostgreSQL COPY command.
        
        Args:
            table_name (str): Target table name
            columns (list): List of column names
            data (list): List of data tuples
            schema (str, optional): Schema name (defaults to current schema)
            
        Returns:
            int: Number of copied rows
            
        Example:
            rows_copied = db_manager.execute_copy(
                "users",
                ["name", "email"],
                [("John", "john@example.com"), ("Jane", "jane@example.com")]
            )
        """
        use_schema = schema or self.schema
        column_list = ', '.join(columns)
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Create temporary table
                    temp_table = f"temp_copy_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    cursor.execute(f"""
                        CREATE TEMP TABLE {temp_table} 
                        AS SELECT {column_list} 
                        FROM {use_schema}.{table_name} 
                        WITH NO DATA
                    """)
                    
                    # Copy data to temporary table
                    from io import StringIO
                    output = StringIO()
                    for row in data:
                        output.write('\t'.join([str(val) for val in row]) + '\n')
                    output.seek(0)
                    
                    cursor.copy_from(output, temp_table, columns=columns)
                    
                    # Insert from temporary table to target table
                    cursor.execute(f"""
                        INSERT INTO {use_schema}.{table_name} ({column_list})
                        SELECT {column_list} FROM {temp_table}
                    """)
                    
                    return cursor.rowcount
                    
                finally:
                    # Cleanup temporary table
                    cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")

    def listen_notify(self, 
                     channel: str, 
                     callback: callable,
                     timeout: Optional[float] = None):
        """
        Listens for PostgreSQL notifications.
        
        Args:
            channel (str): Notification channel name
            callback (callable): Function to call when notification is received
            timeout (float, optional): Timeout in seconds
            
        Example:
            def handle_notification(pid, channel, payload):
                print(f"Received: {payload} on channel {channel} from pid {pid}")
                
            db_manager.listen_notify("user_updates", handle_notification, timeout=60)
        """
        with self.get_connection() as conn:
            conn.set_isolation_level(0)  # ISOLATION_LEVEL_AUTOCOMMIT
            
            with conn.cursor() as cursor:
                cursor.execute(f"LISTEN {channel}")
                
                while True:
                    if select.select([conn], [], [], timeout) == ([], [], []):
                        self.logger.debug("Listen timeout, checking for notifications...")
                        continue
                        
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop()
                        callback(notify.pid, notify.channel, notify.payload)

# Usage Example
def postgresql_production_example():
    """Demonstrates production usage of the PostgreSQL database manager."""
    
    # Configuration
    config_override = {
        "SERVER": "prod-server",
        "DATABASE_NAME": "ProductionDB",
        "PORT_NUMBER": 5432,
        "SCHEMA": "analytics"
    }
    
    # Initialize manager
    db_manager = PostgreSQLDatabaseManager(config_override)
    
    try:
        # Query with server-side cursor
        for user in db_manager.execute_query(
            "SELECT * FROM users WHERE active = %s",
            (True,),
            fetch_size=1000
        ):
            process_user(user)
        
        # Batch insert with COPY
        new_users = [
            ("John Doe", "john@example.com", "IT"),
            ("Jane Smith", "jane@example.com", "HR")
        ]
        rows_copied = db_manager.execute_copy(
            "users",
            ["name", "email", "department"],
            new_users
        )
        print(f"Copied {rows_copied} users")
        
        # Transaction with SERIALIZABLE isolation
        with db_manager.transaction("SERIALIZABLE") as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_balances 
                    SET balance = balance + %s 
                    WHERE user_id = %s
                """, (100.00, 1))
        
    except Exception as e:
        print(f"Error in production example: {str(e)}")
```

[🔝 Back to Table of Contents](#table-of-contents)

#### 3. Production-Ready MySQL Implementation
```python
from typing import Optional, Dict, Any, List, Union, Generator
import logging
from contextlib import contextmanager
from datetime import datetime
import csv
import tempfile

class MySQLDatabaseManager:
    """Production-ready MySQL database manager implementation."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = MYSQL["MYSQL"]
        self._init_error_handlers()
        if config_override:
            self._apply_config_override(config_override)

    def _init_error_handlers(self):
        """Initialize MySQL-specific error handlers and reconnection logic."""
        self.retryable_errors = (
            "MySQL server has gone away",
            "Lost connection to MySQL server",
            "Can't connect to MySQL server",
            "Lock wait timeout exceeded"
        )
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _apply_config_override(self, override: Dict[str, Any]) -> None:
        """
        Applies configuration overrides with MySQL-specific validation.
        
        Args:
            override: Dictionary of configuration overrides
            
        Example:
            {
                "CHARSET": "utf8mb4",
                "COLLATION": "utf8mb4_unicode_ci",
                "MULTI_HOST": 1,
                "COMPRESS": 1
            }
        """
        for key, value in override.items():
            if key in self.config["DEFAULT_PARAMETERS"]:
                self.config["DEFAULT_PARAMETERS"][key] = value
                if key == "CHARSET":
                    # Update collation if charset changes
                    self._update_collation_for_charset(value)
            else:
                self.logger.warning(f"Ignoring unknown MySQL parameter: {key}")

    def _update_collation_for_charset(self, charset: str) -> None:
        """Updates default collation based on charset."""
        charset_collation_map = {
            "utf8mb4": "utf8mb4_unicode_ci",
            "utf8": "utf8_general_ci",
            "latin1": "latin1_swedish_ci"
        }
        if charset in charset_collation_map:
            self.config["DEFAULT_PARAMETERS"]["COLLATION"] = charset_collation_map[charset]

    @contextmanager
    def get_connection(self, auto_reconnect: bool = True):
        """
        Gets a MySQL connection with automatic reconnection support.
        
        Args:
            auto_reconnect (bool): Whether to enable automatic reconnection
            
        Yields:
            pyodbc.Connection: Active database connection
            
        Example:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
                    charset = cursor.fetchone()[1]
        """
        connection = None
        retry_count = 0
        
        while True:
            try:
                connection_string = self.config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MYSQL)
                connection = self.config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](connection_string)()
                
                # Set session variables
                with connection.cursor() as cursor:
                    cursor.execute(f"SET NAMES {self.config['DEFAULT_PARAMETERS']['CHARSET']}")
                    cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
                    cursor.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'")
                
                yield connection
                break
                
            except Exception as e:
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
                
                if not auto_reconnect or not any(err in str(e) for err in self.retryable_errors):
                    raise
                
                retry_count += 1
                if retry_count >= self.max_retries:
                    raise Exception(f"Max retry attempts ({self.max_retries}) exceeded") from e
                
                self.logger.warning(f"Connection attempt {retry_count} failed. Retrying...")
                time.sleep(self.retry_delay * retry_count)
                
            finally:
                if connection:
                    try:
                        connection.close()
                    except Exception as e:
                        self.logger.error(f"Error closing connection: {str(e)}")

    @contextmanager
    def transaction(self, isolation_level: Optional[str] = None):
        """
        Manages MySQL transaction with specific isolation level.
        
        Args:
            isolation_level (str, optional): Transaction isolation level
                (READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE)
                
        Example:
            with db_manager.transaction("REPEATABLE READ") as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO orders (user_id, amount) VALUES (%s, %s)",
                        (1, 100.00)
                    )
        """
        with self.get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    if isolation_level:
                        cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                    
                    cursor.execute("START TRANSACTION")
                    
                yield connection
                connection.commit()
                
            except Exception as e:
                connection.rollback()
                self.logger.error(f"Transaction failed: {str(e)}")
                raise

    def execute_query(self, 
                     query: str, 
                     params: Optional[tuple] = None,
                     buffer_results: bool = False) -> Union[List[Dict[str, Any]], Generator]:
        """
        Executes a query with optional result buffering.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            buffer_results (bool): Whether to buffer results in memory
            
        Returns:
            Union[List[Dict], Generator]: Query results
            
        Example:
            # Buffered results
            users = db_manager.execute_query(
                "SELECT * FROM users WHERE department = %s",
                ("IT",),
                buffer_results=True
            )
            
            # Unbuffered results
            for user in db_manager.execute_query(
                "SELECT * FROM large_table",
                buffer_results=False
            ):
                process_user(user)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(buffered=buffer_results)
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                columns = [column[0] for column in cursor.description]
                
                if buffer_results:
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                else:
                    while True:
                        row = cursor.fetchone()
                        if not row:
                            break
                        yield dict(zip(columns, row))
                        
            finally:
                cursor.close()

    def bulk_load_data(self, 
                      table_name: str, 
                      data: List[tuple],
                      columns: List[str],
                      batch_size: int = 10000) -> int:
        """
        Efficiently loads data using MySQL LOAD DATA LOCAL INFILE.
        
        Args:
            table_name (str): Target table name
            data (list): List of data tuples
            columns (list): List of column names
            batch_size (int): Number of rows per batch
            
        Returns:
            int: Number of loaded rows
            
        Example:
            rows_loaded = db_manager.bulk_load_data(
                "users",
                [("John", "IT"), ("Jane", "HR")],
                ["name", "department"]
            )
        """
        total_rows = 0
        
        with tempfile.NamedTemporaryFile(mode='w', newline='', delete=False) as temp_file:
            writer = csv.writer(temp_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            
            # Write data in batches
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                writer.writerows(batch)
                
            temp_file_path = temp_file.name
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Enable local infile loading
                    cursor.execute("SET GLOBAL local_infile = 1")
                    
                    # Load data from temp file
                    load_sql = f"""
                        LOAD DATA LOCAL INFILE '{temp_file_path}'
                        INTO TABLE {table_name}
                        FIELDS TERMINATED BY '\t'
                        LINES TERMINATED BY '\n'
                        ({', '.join(columns)})
                    """
                    cursor.execute(load_sql)
                    total_rows = cursor.rowcount
                    
        finally:
            import os
            os.unlink(temp_file_path)
        
        return total_rows

# Usage Example
def mysql_production_example():
    """Demonstrates production usage of the MySQL database manager."""
    
    # Configuration
    config_override = {
        "SERVER": "prod-server",
        "DATABASE_NAME": "ProductionDB",
        "PORT_NUMBER": 3306,
        "CHARSET": "utf8mb4",
        "MULTI_HOST": 1
    }
    
    # Initialize manager
    db_manager = MySQLDatabaseManager(config_override)
    
    try:
        # Unbuffered query for large result sets
        for user in db_manager.execute_query(
            "SELECT * FROM users WHERE status = %s",
            ("active",),
            buffer_results=False
        ):
            process_user(user)
        
        # Bulk data loading
        new_orders = [
            (1, "Product A", 100.00),
            (2, "Product B", 150.00),
            (3, "Product C", 200.00)
        ]
        rows_loaded = db_manager.bulk_load_data(
            "orders",
            new_orders,
            ["user_id", "product_name", "amount"]
        )
        print(f"Loaded {rows_loaded} orders")
        
        # Transaction with specific isolation level
        with db_manager.transaction("REPEATABLE READ") as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_balances 
                    SET balance = balance - %s 
                    WHERE user_id = %s AND balance >= %s
                """, (50.00, 1, 50.00))
        
    except Exception as e:
        print(f"Error in production example: {str(e)}")
```

[🔝 Back to Table of Contents](#table-of-contents)

#### 4. Production-Ready SQLite3 Implementation
```python
from typing import Optional, Dict, Any, List, Union, Generator
import logging
from contextlib import contextmanager
import os
import time
import sqlite3
from pathlib import Path
import shutil
import threading

class SQLite3DatabaseManager:
    """Production-ready SQLite3 database manager implementation."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = SQLITE3["SQLITE3"]
        self._connection_lock = threading.Lock()
        self._init_pragmas()
        if config_override:
            self._apply_config_override(config_override)

    def _init_pragmas(self):
        """Initialize default SQLite3 pragmas for optimal performance and safety."""
        self.default_pragmas = {
            "journal_mode": "WAL",          # Write-Ahead Logging for better concurrency
            "synchronous": "NORMAL",        # Balance between safety and performance
            "foreign_keys": "ON",           # Enforce foreign key constraints
            "cache_size": -2000,           # Use 2MB of memory for page cache
            "temp_store": "MEMORY",        # Store temp tables and indices in memory
            "mmap_size": 268435456,        # Memory-mapped I/O (256MB)
            "busy_timeout": 5000           # Wait up to 5 seconds on locks
        }

    def _apply_config_override(self, override: Dict[str, Any]) -> None:
        """
        Applies configuration overrides with SQLite-specific validation.
        
        Args:
            override: Dictionary of configuration overrides
            
        Example:
            {
                "FULLY_QUALIFIED_PATH": "/data/sqlite",
                "DATABASE_NAME": "production.db",
                "PRAGMAS": {
                    "journal_mode": "DELETE",
                    "synchronous": "FULL"
                }
            }
        """
        for key, value in override.items():
            if key == "PRAGMAS":
                self.default_pragmas.update(value)
            elif key in self.config["DEFAULT_PARAMETERS"]:
                self.config["DEFAULT_PARAMETERS"][key] = value
            else:
                self.logger.warning(f"Ignoring unknown SQLite parameter: {key}")

    def _get_database_path(self) -> str:
        """Constructs full database path from configuration."""
        base_path = self.config["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"]
        db_name = self.config["DEFAULT_PARAMETERS"]["DATABASE_NAME"]
        return os.path.join(base_path, db_name)

    def _init_database(self, connection) -> None:
        """Initializes database with configured pragmas."""
        with connection.cursor() as cursor:
            for pragma, value in self.default_pragmas.items():
                cursor.execute(f"PRAGMA {pragma} = {value}")

    def backup_database(self, backup_path: str) -> None:
        """
        Creates a backup of the database with proper locking.
        
        Args:
            backup_path: Path for backup file
            
        Example:
            db_manager.backup_database("/backups/mydb_backup.db")
        """
        source_path = self._get_database_path()
        
        with self._connection_lock:
            # Ensure WAL is checkpointed
            with self.get_connection() as conn:
                conn.execute("PRAGMA wal_checkpoint(FULL)")
            
            # Copy database file and WAL
            shutil.copy2(source_path, backup_path)
            wal_file = f"{source_path}-wal"
            if os.path.exists(wal_file):
                shutil.copy2(wal_file, f"{backup_path}-wal")

    def vacuum_database(self) -> None:
        """
        Performs database vacuum operation to reclaim space.
        
        Example:
            db_manager.vacuum_database()
        """
        with self.get_connection() as conn:
            conn.execute("VACUUM")

    @contextmanager
    def get_connection(self, read_only: bool = False):
        """
        Gets a SQLite connection with proper locking and optimizations.
        
        Args:
            read_only (bool): Whether to open database in read-only mode
            
        Yields:
            sqlite3.Connection: Active database connection
            
        Example:
            with db_manager.get_connection(read_only=True) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
        """
        connection = None
        
        try:
            uri = f"file:{self._get_database_path()}"
            if read_only:
                uri += "?mode=ro"
            
            with self._connection_lock:
                connection = sqlite3.connect(
                    uri,
                    uri=True,
                    timeout=self.default_pragmas["busy_timeout"] / 1000,
                    isolation_level=None  # Enable autocommit mode for explicit transaction control
                )
                
                # Enable modern features
                connection.row_factory = sqlite3.Row
                
                # Initialize pragmas
                self._init_database(connection)
                
                yield connection
                
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {str(e)}")

    @contextmanager
    def transaction(self, isolation_level: str = "DEFERRED"):
        """
        Manages SQLite transaction with specific isolation level.
        
        Args:
            isolation_level (str): Transaction isolation level
                (DEFERRED, IMMEDIATE, or EXCLUSIVE)
                
        Example:
            with db_manager.transaction("IMMEDIATE") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name) VALUES (?)",
                    ("John",)
                )
        """
        with self.get_connection() as connection:
            try:
                connection.execute(f"BEGIN {isolation_level} TRANSACTION")
                yield connection
                connection.execute("COMMIT")
            except Exception as e:
                connection.execute("ROLLBACK")
                self.logger.error(f"Transaction failed: {str(e)}")
                raise

    def execute_query(self, 
                     query: str, 
                     params: Optional[tuple] = None,
                     chunk_size: Optional[int] = None) -> Union[List[Dict[str, Any]], Generator]:
        """
        Executes a query with optional result chunking.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            chunk_size (int, optional): Number of rows per chunk
            
        Returns:
            Union[List[Dict], Generator]: Query results
            
        Example:
            # Get all results
            users = db_manager.execute_query(
                "SELECT * FROM users WHERE age > ?",
                (18,)
            )
            
            # Process in chunks
            for chunk in db_manager.execute_query(
                "SELECT * FROM large_table",
                chunk_size=1000
            ):
                process_chunk(chunk)
        """
        with self.get_connection(read_only=query.strip().upper().startswith("SELECT")) as conn:
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if chunk_size:
                    while True:
                        rows = cursor.fetchmany(chunk_size)
                        if not rows:
                            break
                        yield [dict(row) for row in rows]
                else:
                    return [dict(row) for row in cursor.fetchall()]
                    
            finally:
                cursor.close()

    def bulk_insert(self, 
                   table_name: str,
                   data: List[Dict[str, Any]],
                   batch_size: int = 1000) -> int:
        """
        Efficiently inserts large amounts of data.
        
        Args:
            table_name (str): Target table name
            data (List[Dict]): List of data dictionaries
            batch_size (int): Number of rows per batch
            
        Returns:
            int: Number of inserted rows
            
        Example:
            users = [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ]
            rows_inserted = db_manager.bulk_insert("users", users)
        """
        if not data:
            return 0
            
        # Extract column names from first row
        columns = list(data[0].keys())
        placeholders = ",".join("?" * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        total_rows = 0
        with self.transaction("IMMEDIATE") as conn:
            cursor = conn.cursor()
            
            try:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    values = [[row[col] for col in columns] for row in batch]
                    cursor.executemany(insert_sql, values)
                    total_rows += cursor.rowcount
                    
                return total_rows
                
            finally:
                cursor.close()

# Usage Example
def sqlite3_production_example():
    """Demonstrates production usage of the SQLite3 database manager."""
    
    # Configuration
    config_override = {
        "FULLY_QUALIFIED_PATH": "/data/sqlite",
        "DATABASE_NAME": "production.db",
        "PRAGMAS": {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "cache_size": -4000  # 4MB cache
        }
    }
    
    # Initialize manager
    db_manager = SQLite3DatabaseManager(config_override)
    
    try:
        # Create backup before operations
        db_manager.backup_database("/backups/prod_backup.db")
        
        # Process large table in chunks
        for chunk in db_manager.execute_query(
            "SELECT * FROM transaction_history",
            chunk_size=1000
        ):
            process_transaction_chunk(chunk)
        
        # Bulk insert with transaction
        new_orders = [
            {"user_id": 1, "product": "A", "amount": 100},
            {"user_id": 2, "product": "B", "amount": 150}
        ]
        rows_inserted = db_manager.bulk_insert(
            "orders",
            new_orders,
            batch_size=500
        )
        print(f"Inserted {rows_inserted} orders")
        
        # Execute write operations in exclusive transaction
        with db_manager.transaction("EXCLUSIVE") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_balances 
                SET balance = balance - ?
                WHERE user_id = ? AND balance >= ?
            """, (50.00, 1, 50.00))
            
            if cursor.rowcount == 0:
                raise ValueError("Insufficient balance")
        
        # Vacuum database after large deletions
        db_manager.vacuum_database()
        
    except Exception as e:
        print(f"Error in production example: {str(e)}")
```

[🔝 Back to Table of Contents](#table-of-contents)

#### 5. Production-Ready DuckDB Implementation
```python
from typing import Optional, Dict, Any, List, Union, Generator
import logging
from contextlib import contextmanager
import os
import pandas as pd
import numpy as np
from datetime import datetime
import threading

class DuckDBManager:
    """Production-ready DuckDB manager implementation optimized for analytics."""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = DUCKDB["DUCKDB"]
        self._connection_lock = threading.Lock()
        self._init_settings()
        if config_override:
            self._apply_config_override(config_override)

    def _init_settings(self):
        """Initialize default DuckDB settings for optimal analytics performance."""
        self.default_settings = {
            "memory_limit": "8GB",                  # Maximum memory usage
            "threads": "auto",                      # Automatic thread configuration
            "default_order": "ASC",                # Default ordering
            "preserve_insertion_order": "false",    # Optimize for analytics
            "temp_directory": "/tmp/duckdb",       # Temporary file location
            "compression": "true",                 # Enable compression
            "checkpoint_on_shutdown": "true",      # Ensure data persistence
            "external_threads": "4"                # Threads for external operations
        }

    def _apply_config_override(self, override: Dict[str, Any]) -> None:
        """
        Applies configuration overrides with DuckDB-specific validation.
        
        Args:
            override: Dictionary of configuration overrides
            
        Example:
            {
                "FULLY_QUALIFIED_PATH": "/data/duckdb",
                "DATABASE_NAME": "analytics.duckdb",
                "SETTINGS": {
                    "memory_limit": "16GB",
                    "threads": "8"
                }
            }
        """
        for key, value in override.items():
            if key == "SETTINGS":
                self.default_settings.update(value)
            elif key in self.config["DEFAULT_PARAMETERS"]:
                self.config["DEFAULT_PARAMETERS"][key] = value
            else:
                self.logger.warning(f"Ignoring unknown DuckDB parameter: {key}")

    def _get_database_path(self) -> str:
        """Constructs full database path from configuration."""
        base_path = self.config["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"]
        db_name = self.config["DEFAULT_PARAMETERS"]["DATABASE_NAME"]
        return os.path.join(base_path, db_name)

    def _init_database(self, connection) -> None:
        """Initializes database with configured settings and extensions."""
        for setting, value in self.default_settings.items():
            connection.execute(f"SET {setting}='{value}'")
        
        # Load common extensions
        extensions = [
            "httpfs",      # HTTP file system access
            "parquet",     # Parquet file support
            "json",        # JSON processing
            "excel",       # Excel file support
            "icu"         # International Components for Unicode
        ]
        
        for extension in extensions:
            connection.execute(f"INSTALL '{extension}'; LOAD '{extension}';")

    @contextmanager
    def get_connection(self, read_only: bool = False):
        """
        Gets a DuckDB connection with analytics optimizations.
        
        Args:
            read_only (bool): Whether to open database in read-only mode
            
        Yields:
            duckdb.DuckDBPyConnection: Active database connection
            
        Example:
            with db_manager.get_connection(read_only=True) as conn:
                result = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        """
        connection = None
        
        try:
            db_path = self._get_database_path()
            
            with self._connection_lock:
                connection = self.config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](
                    db_path + "?access_mode=READ_ONLY" if read_only else db_path
                )()
                
                # Initialize settings and extensions
                self._init_database(connection)
                
                yield connection
                
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {str(e)}")

    def execute_analytics_query(self, 
                              query: str, 
                              params: Optional[Dict[str, Any]] = None,
                              return_type: str = 'dataframe') -> Union[pd.DataFrame, List[Dict], Any]:
        """
        Executes analytics query with optimized output handling.
        
        Args:
            query (str): SQL query to execute
            params (dict, optional): Named parameters
            return_type (str): Output format ('dataframe', 'dict', 'arrow', 'raw')
            
        Returns:
            Query results in specified format
            
        Example:
            # Get results as DataFrame
            df = db_manager.execute_analytics_query(
                """
                SELECT 
                    date_trunc('month', order_date) as month,
                    SUM(amount) as total_sales
                FROM orders
                GROUP BY 1
                ORDER BY 1
                """,
                return_type='dataframe'
            )
        """
        with self.get_connection(read_only=True) as conn:
            try:
                if params:
                    result = conn.execute(query, parameters=params)
                else:
                    result = conn.execute(query)
                
                if return_type == 'dataframe':
                    return result.df()
                elif return_type == 'dict':
                    df = result.df()
                    return df.to_dict('records')
                elif return_type == 'arrow':
                    return result.arrow()
                else:
                    return result.fetchall()
                    
            except Exception as e:
                self.logger.error(f"Query execution failed: {str(e)}")
                raise

    def load_data(self, 
                 table_name: str,
                 data_source: Union[str, pd.DataFrame],
                 file_type: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None) -> int:
        """
        Efficiently loads data from various sources into DuckDB.
        
        Args:
            table_name (str): Target table name
            data_source: File path or DataFrame
            file_type (str, optional): Type of file ('parquet', 'csv', etc.)
            options (dict, optional): Loading options
            
        Returns:
            int: Number of loaded rows
            
        Example:
            # Load Parquet file
            rows = db_manager.load_data(
                "sales",
                "s3://bucket/sales.parquet",
                "parquet",
                {"compression": "snappy"}
            )
            
            # Load DataFrame
            df = pd.read_csv("local_data.csv")
            rows = db_manager.load_data("local_sales", df)
        """
        with self.get_connection() as conn:
            try:
                if isinstance(data_source, pd.DataFrame):
                    conn.register("temp_view", data_source)
                    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_view")
                    return len(data_source)
                
                elif isinstance(data_source, str):
                    if not file_type:
                        file_type = os.path.splitext(data_source)[1][1:]
                    
                    options_str = ""
                    if options:
                        options_str = "(" + ", ".join(f"{k}='{v}'" for k, v in options.items()) + ")"
                    
                    query = f"""
                        CREATE TABLE {table_name} AS 
                        SELECT * FROM read_{file_type}(
                            '{data_source}'{options_str}
                        )
                    """
                    conn.execute(query)
                    return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                
                else:
                    raise ValueError("data_source must be DataFrame or file path")
                    
            except Exception as e:
                self.logger.error(f"Data loading failed: {str(e)}")
                raise

    def create_materialized_view(self,
                               view_name: str,
                               query: str,
                               refresh_interval: Optional[int] = None) -> None:
        """
        Creates and manages materialized views for analytics.
        
        Args:
            view_name (str): Name of materialized view
            query (str): Query defining the view
            refresh_interval (int, optional): Refresh interval in minutes
            
        Example:
            db_manager.create_materialized_view(
                "daily_sales",
                '''
                SELECT 
                    date_trunc('day', order_date) as day,
                    SUM(amount) as total_sales,
                    COUNT(DISTINCT user_id) as unique_customers
                FROM orders
                GROUP BY 1
                ''',
                refresh_interval=60  # Refresh hourly
            )
        """
        with self.get_connection() as conn:
            try:
                # Create materialized view
                conn.execute(f"CREATE MATERIALIZED VIEW {view_name} AS {query}")
                
                if refresh_interval:
                    # Schedule refresh
                    conn.execute(f"""
                        CREATE TASK {view_name}_refresh
                        INTERVAL {refresh_interval} MINUTES
                        AS REFRESH MATERIALIZED VIEW {view_name}
                    """)
                    
            except Exception as e:
                self.logger.error(f"Failed to create materialized view: {str(e)}")
                raise

    def analyze_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """
        Analyzes and returns detailed table statistics.
        
        Args:
            table_name (str): Name of table to analyze
            
        Returns:
            dict: Comprehensive statistics about the table
            
        Example:
            stats = db_manager.analyze_table_statistics("orders")
            print(f"Total rows: {stats['row_count']}")
            print(f"Size on disk: {stats['size_mb']}MB")
        """
        queries = {
            "row_count": f"SELECT COUNT(*) FROM {table_name}",
            "column_stats": f"""
                SELECT 
                    column_name,
                    data_type,
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT {{}}) as unique_values,
                    SUM(CASE WHEN {{}} IS NULL THEN 1 ELSE 0 END) as null_count
                FROM {table_name}
                GROUP BY 1, 2
            """,
            "size": f"SELECT pg_total_relation_size('{table_name}')"
        }
        
        stats = {}
        with self.get_connection(read_only=True) as conn:
            try:
                # Get basic stats
                stats["row_count"] = conn.execute(queries["row_count"]).fetchone()[0]
                stats["size_mb"] = conn.execute(queries["size"]).fetchone()[0] / (1024 * 1024)
                
                # Get column-level statistics
                column_info = conn.execute(f"DESCRIBE {table_name}").df()
                stats["columns"] = {}
                
                for _, row in column_info.iterrows():
                    col_name = row["column_name"]
                    col_stats = conn.execute(
                        queries["column_stats"].format(col_name, col_name)
                    ).fetchone()
                    
                    stats["columns"][col_name] = {
                        "data_type": row["column_type"],
                        "unique_values": col_stats[3],
                        "null_count": col_stats[4],
                        "null_percentage": (col_stats[4] / col_stats[2]) * 100
                    }
                
                return stats
                
            except Exception as e:
                self.logger.error(f"Failed to analyze table statistics: {str(e)}")
                raise

# Usage Example
def duckdb_analytics_example():
    """Demonstrates production analytics usage of the DuckDB manager."""
    
    # Configuration
    config_override = {
        "FULLY_QUALIFIED_PATH": "/data/duckdb",
        "DATABASE_NAME": "analytics.duckdb",
        "SETTINGS": {
            "memory_limit": "32GB",
            "threads": "16"
        }
    }
    
    # Initialize manager
    db_manager = DuckDBManager(config_override)
    
    try:
        # Load data from various sources
        db_manager.load_data(
            "sales_2023",
            "s3://analytics/sales_2023.parquet",
            "parquet",
            {"compression": "snappy"}
        )
        
        # Create materialized view for common analytics
        db_manager.create_materialized_view(
            "monthly_metrics",
            """
            SELECT 
                date_trunc('month', order_date) as month,
                COUNT(DISTINCT user_id) as monthly_active_users,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_order_value,
                APPROX_COUNT_DISTINCT(product_id) as unique_products_sold
            FROM sales_2023
            GROUP BY 1
            ORDER BY 1
            """,
            refresh_interval=120  # Refresh every 2 hours
        )
        
        # Run analytics query
        metrics_df = db_manager.execute_analytics_query(
            """
            WITH customer_segments AS (
                SELECT 
                    user_id,
                    SUM(amount) as total_spent,
                    COUNT(*) as order_count,
                    MIN(order_date) as first_order,
                    MAX(order_date) as last_order
                FROM sales_2023
                GROUP BY 1
            )
            SELECT 
                CASE 
                    WHEN total_spent >= 1000 THEN 'High Value'
                    WHEN total_spent >= 500 THEN 'Medium Value'
                    ELSE 'Low Value'
                END as customer_segment,
                COUNT(*) as customer_count,
                AVG(total_spent) as avg_customer_value,
                AVG(order_count) as avg_orders_per_customer,
                AVG(DATEDIFF('day', first_order, last_order)) as avg_customer_lifetime_days
            FROM customer_segments
            GROUP BY 1
            ORDER BY AVG(total_spent) DESC
            """,
            return_type='dataframe'
        )
        
        print("Customer Segment Analysis:")
        print(metrics_df)
        
        # Analyze table statistics
        stats = db_manager.analyze_table_statistics("sales_2023")
        print("\nTable Statistics:")
        print(f"Total Rows: {stats['row_count']:,}")
        print(f"Size on Disk: {stats['size_mb']:.2f}MB")
        
    except Exception as e:
        print(f"Error in analytics example: {str(e)}")
```

[🔝 Back to Table of Contents](#table-of-contents)

### Database Utilities and Common Features

#### 1. Connection Pool Manager
```python
from typing import Optional, Dict, Any, List, Callable
import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PooledConnection:
    """Represents a connection in the pool."""
    connection: Any
    created_at: datetime
    last_used: datetime
    uses: int = 0
    is_healthy: bool = True

class ConnectionPoolManager:
    """Manages connection pools for all database types."""
    
    def __init__(self, 
                 pool_size: int = 10,
                 max_overflow: int = 5,
                 timeout: int = 30,
                 max_age: int = 3600,
                 max_uses: int = 10000):
        """
        Initialize connection pool manager.
        
        Args:
            pool_size: Base size of the connection pool
            max_overflow: Maximum additional connections
            timeout: Seconds to wait for connection
            max_age: Maximum age of connection in seconds
            max_uses: Maximum number of times to use a connection
        """
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        self.max_age = max_age
        self.max_uses = max_uses
        
        self.pools: Dict[str, queue.Queue] = {}
        self.overflow_connections: Dict[str, int] = {}
        self.lock = threading.RLock()
        
        # Start maintenance thread
        self.maintenance_thread = threading.Thread(
            target=self._pool_maintenance,
            daemon=True
        )
        self.maintenance_thread.start()

    def get_connection(self, db_type: str, creator: Callable) -> Any:
        """
        Get a connection from the pool or create new one.
        
        Args:
            db_type: Type of database connection
            creator: Function to create new connection
            
        Returns:
            Database connection
            
        Example:
            connection = pool_manager.get_connection(
                'postgresql',
                lambda: create_postgresql_connection()
            )
        """
        with self.lock:
            if db_type not in self.pools:
                self.pools[db_type] = queue.Queue(self.pool_size)
                self.overflow_connections[db_type] = 0
            
            pool = self.pools[db_type]
            
            try:
                # Try to get connection from pool
                pooled_conn = pool.get_nowait()
                
                # Check if connection is still valid
                if self._is_connection_valid(pooled_conn):
                    pooled_conn.last_used = datetime.now()
                    pooled_conn.uses += 1
                    return pooled_conn.connection
                else:
                    self._close_connection(pooled_conn)
            
            except queue.Empty:
                # Create new connection if within limits
                if pool.qsize() + self.overflow_connections[db_type] < self.pool_size + self.max_overflow:
                    self.overflow_connections[db_type] += 1
                    return self._create_pooled_connection(creator).connection
                
                # Wait for available connection
                try:
                    pooled_conn = pool.get(timeout=self.timeout)
                    if self._is_connection_valid(pooled_conn):
                        pooled_conn.last_used = datetime.now()
                        pooled_conn.uses += 1
                        return pooled_conn.connection
                    else:
                        self._close_connection(pooled_conn)
                        return self._create_pooled_connection(creator).connection
                except queue.Empty:
                    raise TimeoutError("Connection pool timeout")

    def return_connection(self, db_type: str, connection: Any) -> None:
        """
        Return a connection to the pool.
        
        Args:
            db_type: Type of database connection
            connection: Connection to return
            
        Example:
            pool_manager.return_connection('postgresql', connection)
        """
        with self.lock:
            pool = self.pools[db_type]
            
            # Create PooledConnection if it's a raw connection
            if not isinstance(connection, PooledConnection):
                connection = PooledConnection(
                    connection=connection,
                    created_at=datetime.now(),
                    last_used=datetime.now()
                )
            
            try:
                pool.put_nowait(connection)
                if self.overflow_connections[db_type] > 0:
                    self.overflow_connections[db_type] -= 1
            except queue.Full:
                self._close_connection(connection)

    def _create_pooled_connection(self, creator: Callable) -> PooledConnection:
        """Creates new pooled connection."""
        return PooledConnection(
            connection=creator(),
            created_at=datetime.now(),
            last_used=datetime.now()
        )

    def _is_connection_valid(self, pooled_conn: PooledConnection) -> bool:
        """Checks if a pooled connection is still valid."""
        if not pooled_conn.is_healthy:
            return False
            
        now = datetime.now()
        
        # Check age
        if (now - pooled_conn.created_at).total_seconds() > self.max_age:
            return False
            
        # Check uses
        if pooled_conn.uses >= self.max_uses:
            return False
            
        # Test connection
        try:
            self._test_connection(pooled_conn.connection)
            return True
        except Exception:
            return False

    def _test_connection(self, connection: Any) -> bool:
        """Tests if connection is still alive."""
        try:
            if hasattr(connection, 'ping'):
                connection.ping()
            else:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    def _close_connection(self, pooled_conn: PooledConnection) -> None:
        """Closes a pooled connection."""
        try:
            pooled_conn.connection.close()
        except Exception:
            pass
        finally:
            pooled_conn.is_healthy = False

    def _pool_maintenance(self) -> None:
        """Maintenance thread to clean up old connections."""
        while True:
            time.sleep(60)  # Run every minute
            
            with self.lock:
                for db_type, pool in self.pools.items():
                    healthy_connections = queue.Queue(self.pool_size)
                    
                    # Check all connections in the pool
                    while not pool.empty():
                        try:
                            conn = pool.get_nowait()
                            if self._is_connection_valid(conn):
                                healthy_connections.put(conn)
                            else:
                                self._close_connection(conn)
                        except queue.Empty:
                            break
                    
                    # Replace pool with healthy connections
                    self.pools[db_type] = healthy_connections
                    
                    # Reset overflow count
                    self.overflow_connections[db_type] = 0

    def close_all(self) -> None:
        """Closes all connections in all pools."""
        with self.lock:
            for pool in self.pools.values():
                while not pool.empty():
                    try:
                        conn = pool.get_nowait()
                        self._close_connection(conn)
                    except queue.Empty:
                        break
            self.pools.clear()
            self.overflow_connections.clear()
```

#### 2. Query Profiler and Monitoring
```python
from functools import wraps
import time
import statistics
from typing import Optional, Dict, List, Any
import json

class QueryProfiler:
    """Profiles and monitors database queries."""
    
    def __init__(self, 
                 slow_query_threshold: float = 1.0,
                 log_file: Optional[str] = None):
        """
        Initialize query profiler.
        
        Args:
            slow_query_threshold: Seconds to consider query as slow
            log_file: Path to log file for query statistics
        """
        self.slow_query_threshold = slow_query_threshold
        self.log_file = log_file
        self.query_stats: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.Lock()

    def __call__(self, func):
        """Decorator for query execution methods."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            query = args[1] if len(args) > 1 else kwargs.get('query', 'Unknown')
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration = time.time() - start_time
                self._record_query(query, duration, error)
        
        return wrapper

    def _record_query(self, 
                     query: str, 
                     duration: float, 
                     error: Optional[str]) -> None:
        """Records query execution statistics."""
        with self.lock:
            normalized_query = self._normalize_query(query)
            
            if normalized_query not in self.query_stats:
                self.query_stats[normalized_query] = []
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'duration': duration,
                'error': error,
                'is_slow': duration > self.slow_query_threshold
            }
            
            self.query_stats[normalized_query].append(stats)
            
            if self.log_file and stats['is_slow']:
                self._log_slow_query(normalized_query, stats)

    def _normalize_query(self, query: str) -> str:
        """Normalizes query for aggregation."""
        # Replace literal values with placeholders
        import re
        query = re.sub(r'\b\d+\b', '?', query)
        query = re.sub(r"'[^']*'", '?', query)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        return query

    def _log_slow_query(self, 
                       query: str, 
                       stats: Dict[str, Any]) -> None:
        """Logs slow query information."""
        with open(self.log_file, 'a') as f:
            log_entry = {
                'query': query,
                'stats': stats
            }
            f.write(json.dumps(log_entry) + '\n')

    def get_query_statistics(self, 
                           query: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for queries.
        
        Args:
            query: Optional specific query to get stats for
            
        Returns:
            Dictionary of query statistics
            
        Example:
            stats = profiler.get_query_statistics()
            print(f"Slow queries: {stats['total_slow_queries']}")
        """
        with self.lock:
            if query:
                normalized_query = self._normalize_query(query)
                stats = self.query_stats.get(normalized_query, [])
            else:
                stats = [stat for query_stats in self.query_stats.values()
                        for stat in query_stats]
            
            if not stats:
                return {"message": "No query statistics available"}
            
            durations = [stat['duration'] for stat in stats]
            errors = [stat for stat in stats if stat['error']]
            slow_queries = [stat for stat in stats if stat['is_slow']]
            
            return {
                "total_queries": len(stats),
                "total_errors": len(errors),
                "total_slow_queries": len(slow_queries),
                "average_duration": statistics.mean(durations),
                "median_duration": statistics.median(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "percentile_95": statistics.quantiles(durations, n=20)[18],
                "error_rate": len(errors) / len(stats) * 100,
                "slow_query_rate": len(slow_queries) / len(stats) * 100
            }

    def reset_statistics(self) -> None:
        """Resets all query statistics."""
        with self.lock:
            self.query_stats.clear()
```

[🔝 Back to Table of Contents](#table-of-contents)

### Advanced Database Operations and Integration Patterns

#### 1. Schema Migration Manager
```python
from typing import Optional, Dict, List, Any
import os
import hashlib
from datetime import datetime
import yaml
from pathlib import Path

class SchemaMigrationManager:
    """Manages database schema migrations across different database types."""
    
    def __init__(self, 
                 migrations_path: str,
                 database_type: str,
                 version_table: str = 'schema_migrations'):
        """
        Initialize migration manager.
        
        Args:
            migrations_path: Path to migration files
            database_type: Type of database
            version_table: Table to track migrations
        """
        self.migrations_path = Path(migrations_path)
        self.database_type = database_type
        self.version_table = version_table
        self.migrations: Dict[str, Dict[str, Any]] = {}
        self._load_migrations()

    def _load_migrations(self) -> None:
        """Loads and validates migration files."""
        if not self.migrations_path.exists():
            raise ValueError(f"Migrations path does not exist: {self.migrations_path}")
        
        # Load migrations from files
        for file_path in sorted(self.migrations_path.glob('*.yaml')):
            with open(file_path) as f:
                migration = yaml.safe_load(f)
                
                # Validate migration format
                required_keys = ['version', 'description', 'up', 'down']
                if not all(key in migration for key in required_keys):
                    raise ValueError(f"Invalid migration format in {file_path}")
                
                # Generate checksum
                migration['checksum'] = self._generate_checksum(migration)
                self.migrations[migration['version']] = migration

    def _generate_checksum(self, migration: Dict[str, Any]) -> str:
        """Generates checksum for migration content."""
        content = f"{migration['version']}{migration['description']}"
        content += ''.join(migration['up'])
        content += ''.join(migration['down'])
        return hashlib.sha256(content.encode()).hexdigest()

    def _ensure_version_table(self, connection) -> None:
        """Creates version table if it doesn't exist."""
        create_table_sql = {
            'postgresql': f"""
                CREATE TABLE IF NOT EXISTS {self.version_table} (
                    version VARCHAR(50) PRIMARY KEY,
                    description TEXT,
                    checksum VARCHAR(64),
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_ms INTEGER
                )
            """,
            'mysql': f"""
                CREATE TABLE IF NOT EXISTS {self.version_table} (
                    version VARCHAR(50) PRIMARY KEY,
                    description TEXT,
                    checksum VARCHAR(64),
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_ms INTEGER
                )
            """,
            'sqlite': f"""
                CREATE TABLE IF NOT EXISTS {self.version_table} (
                    version VARCHAR(50) PRIMARY KEY,
                    description TEXT,
                    checksum VARCHAR(64),
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_ms INTEGER
                )
            """
        }
        
        sql = create_table_sql.get(self.database_type)
        if not sql:
            raise ValueError(f"Unsupported database type: {self.database_type}")
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()

    def get_applied_migrations(self, connection) -> Dict[str, Dict[str, Any]]:
        """Gets list of applied migrations from database."""
        self._ensure_version_table(connection)
        
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT version, checksum FROM {self.version_table}")
            return {row[0]: {'checksum': row[1]} for row in cursor.fetchall()}

    def migrate(self, 
                connection,
                target_version: Optional[str] = None,
                dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        Applies pending migrations.
        
        Args:
            connection: Database connection
            target_version: Optional specific version to migrate to
            dry_run: Whether to actually apply migrations
            
        Returns:
            List of applied migrations
            
        Example:
            applied = migration_manager.migrate(
                connection,
                target_version='1.2.0',
                dry_run=True
            )
            for migration in applied:
                print(f"Would apply: {migration['version']}")
        """
        applied_migrations = self.get_applied_migrations(connection)
        pending_migrations = []
        
        # Determine migrations to apply
        for version, migration in sorted(self.migrations.items()):
            if target_version and version > target_version:
                break
                
            if version not in applied_migrations:
                pending_migrations.append(migration)
            else:
                # Check for modified migrations
                if applied_migrations[version]['checksum'] != migration['checksum']:
                    raise ValueError(
                        f"Migration {version} has been modified after being applied"
                    )
        
        if not pending_migrations:
            return []
        
        # Apply migrations
        applied = []
        for migration in pending_migrations:
            if not dry_run:
                start_time = time.time()
                try:
                    with connection.cursor() as cursor:
                        for statement in migration['up']:
                            cursor.execute(statement)
                        
                        # Record migration
                        cursor.execute(
                            f"""
                            INSERT INTO {self.version_table}
                            (version, description, checksum, duration_ms)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                migration['version'],
                                migration['description'],
                                migration['checksum'],
                                int((time.time() - start_time) * 1000)
                            )
                        )
                        connection.commit()
                        
                except Exception as e:
                    connection.rollback()
                    raise ValueError(
                        f"Failed to apply migration {migration['version']}: {str(e)}"
                    )
            
            applied.append(migration)
        
        return applied

    def rollback(self, 
                 connection,
                 versions: Optional[List[str]] = None,
                 dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        Rolls back applied migrations.
        
        Args:
            connection: Database connection
            versions: Optional specific versions to roll back
            dry_run: Whether to actually apply rollbacks
            
        Returns:
            List of rolled back migrations
            
        Example:
            rolled_back = migration_manager.rollback(
                connection,
                versions=['1.2.0'],
                dry_run=True
            )
        """
        applied_migrations = self.get_applied_migrations(connection)
        to_rollback = []
        
        # Determine migrations to roll back
        if versions:
            for version in versions:
                if version not in applied_migrations:
                    raise ValueError(f"Migration {version} has not been applied")
                if version not in self.migrations:
                    raise ValueError(f"Migration {version} not found")
                to_rollback.append(self.migrations[version])
        else:
            # Roll back last applied migration
            last_version = max(applied_migrations.keys())
            to_rollback.append(self.migrations[last_version])
        
        # Apply rollbacks
        rolled_back = []
        for migration in reversed(to_rollback):
            if not dry_run:
                try:
                    with connection.cursor() as cursor:
                        for statement in migration['down']:
                            cursor.execute(statement)
                        
                        # Remove migration record
                        cursor.execute(
                            f"DELETE FROM {self.version_table} WHERE version = %s",
                            (migration['version'],)
                        )
                        connection.commit()
                        
                except Exception as e:
                    connection.rollback()
                    raise ValueError(
                        f"Failed to roll back migration {migration['version']}: {str(e)}"
                    )
            
            rolled_back.append(migration)
        
        return rolled_back

    def get_migration_status(self, connection) -> Dict[str, Any]:
        """
        Gets detailed migration status.
        
        Returns:
            Dictionary with migration status information
            
        Example:
            status = migration_manager.get_migration_status(connection)
            print(f"Current version: {status['current_version']}")
            print(f"Pending migrations: {status['pending_count']}")
        """
        applied_migrations = self.get_applied_migrations(connection)
        
        current_version = max(applied_migrations.keys()) if applied_migrations else None
        pending_migrations = [
            version for version in self.migrations.keys()
            if version not in applied_migrations
        ]
        
        return {
            "current_version": current_version,
            "total_migrations": len(self.migrations),
            "applied_count": len(applied_migrations),
            "pending_count": len(pending_migrations),
            "pending_migrations": pending_migrations,
            "modified_migrations": [
                version for version, migration in self.migrations.items()
                if version in applied_migrations and
                applied_migrations[version]['checksum'] != migration['checksum']
            ]
        }
```

[🔝 Back to Table of Contents](#table-of-contents)

### Database Monitoring and Health Checks

#### 1. Database Health Monitor
```python
from typing import Optional, Dict, List, Any, Tuple
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import json
from enum import Enum
import psutil

class HealthStatus(Enum):
    """Database health status indicators."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

@dataclass
class HealthMetrics:
    """Stores database health metrics."""
    status: HealthStatus
    connection_count: int
    response_time_ms: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: timedelta
    last_error: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0

class DatabaseHealthMonitor:
    """Monitors database health and performance metrics."""
    
    def __init__(self, 
                 check_interval: int = 60,
                 history_size: int = 1440,  # 24 hours of minute-by-minute data
                 alert_thresholds: Optional[Dict[str, Any]] = None):
        """
        Initialize health monitor.
        
        Args:
            check_interval: Seconds between health checks
            history_size: Number of historical metrics to retain
            alert_thresholds: Custom alert thresholds
        """
        self.check_interval = check_interval
        self.history_size = history_size
        self.metrics_history: List[Tuple[datetime, HealthMetrics]] = []
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Default thresholds
        self.thresholds = {
            'response_time_ms': {
                'warning': 100,
                'critical': 1000
            },
            'connection_count': {
                'warning': 80,  # 80% of max connections
                'critical': 95   # 95% of max connections
            },
            'cpu_usage': {
                'warning': 70,
                'critical': 90
            },
            'memory_usage': {
                'warning': 75,
                'critical': 90
            },
            'disk_usage': {
                'warning': 80,
                'critical': 90
            },
            'error_rate': {
                'warning': 5,    # 5% error rate
                'critical': 10   # 10% error rate
            }
        }
        
        if alert_thresholds:
            self.thresholds.update(alert_thresholds)
        
        # Initialize alert handlers
        self.alert_handlers: List[callable] = []
        
        # Start monitoring thread
        self.should_run = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()

    def add_alert_handler(self, handler: callable) -> None:
        """
        Adds alert handler function.
        
        Args:
            handler: Function to handle alerts
            
        Example:
            def alert_handler(alert_type, message, metrics):
                send_email(f"Database Alert: {alert_type}", message)
                
            monitor.add_alert_handler(alert_handler)
        """
        self.alert_handlers.append(handler)

    def check_health(self, connection) -> HealthMetrics:
        """
        Performs comprehensive health check.
        
        Args:
            connection: Database connection
            
        Returns:
            HealthMetrics object
            
        Example:
            metrics = monitor.check_health(connection)
            print(f"Database Status: {metrics.status.value}")
        """
        try:
            start_time = time.time()
            
            # Test basic connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000
            
            # Get connection count
            connection_count = self._get_connection_count(connection)
            
            # Get system metrics
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Get database uptime
            uptime = self._get_database_uptime(connection)
            
            # Create metrics object
            metrics = HealthMetrics(
                status=HealthStatus.HEALTHY,
                connection_count=connection_count,
                response_time_ms=response_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                uptime=uptime
            )
            
            # Evaluate status based on thresholds
            metrics.status = self._evaluate_health_status(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return HealthMetrics(
                status=HealthStatus.CRITICAL,
                connection_count=0,
                response_time_ms=0,
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                uptime=timedelta(0),
                last_error=str(e),
                error_count=1
            )

    def _get_connection_count(self, connection) -> int:
        """Gets current database connection count."""
        queries = {
            'postgresql': """
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state != 'idle'
            """,
            'mysql': """
                SHOW STATUS 
                WHERE Variable_name = 'Threads_connected'
            """,
            'sqlite': "SELECT 1",  # SQLite is single-connection
            'duckdb': "SELECT 1"   # DuckDB is single-connection
        }
        
        try:
            db_type = connection.__class__.__module__.split('.')[0]
            query = queries.get(db_type, "SELECT 1")
            
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                
                if db_type == 'mysql':
                    return int(result[1])
                elif db_type in ('sqlite', 'duckdb'):
                    return 1
                else:
                    return int(result[0])
                    
        except Exception as e:
            self.logger.error(f"Failed to get connection count: {str(e)}")
            return 0

    def _get_database_uptime(self, connection) -> timedelta:
        """Gets database uptime."""
        queries = {
            'postgresql': "SELECT pg_postmaster_start_time()",
            'mysql': "SHOW STATUS LIKE 'Uptime'",
            'sqlite': "SELECT 1",  # SQLite doesn't track uptime
            'duckdb': "SELECT 1"   # DuckDB doesn't track uptime
        }
        
        try:
            db_type = connection.__class__.__module__.split('.')[0]
            query = queries.get(db_type)
            
            if not query:
                return timedelta(0)
            
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                
                if db_type == 'postgresql':
                    start_time = result[0]
                    return datetime.now() - start_time
                elif db_type == 'mysql':
                    uptime_seconds = int(result[1])
                    return timedelta(seconds=uptime_seconds)
                else:
                    return timedelta(0)
                    
        except Exception as e:
            self.logger.error(f"Failed to get uptime: {str(e)}")
            return timedelta(0)

    def _evaluate_health_status(self, metrics: HealthMetrics) -> HealthStatus:
        """Evaluates overall health status based on metrics."""
        if (metrics.response_time_ms > self.thresholds['response_time_ms']['critical'] or
            metrics.cpu_usage > self.thresholds['cpu_usage']['critical'] or
            metrics.memory_usage > self.thresholds['memory_usage']['critical'] or
            metrics.disk_usage > self.thresholds['disk_usage']['critical'] or
            metrics.error_count > 0):
            return HealthStatus.CRITICAL
            
        elif (metrics.response_time_ms > self.thresholds['response_time_ms']['warning'] or
              metrics.cpu_usage > self.thresholds['cpu_usage']['warning'] or
              metrics.memory_usage > self.thresholds['memory_usage']['warning'] or
              metrics.disk_usage > self.thresholds['disk_usage']['warning'] or
              metrics.warning_count > 0):
            return HealthStatus.DEGRADED
            
        else:
            return HealthStatus.HEALTHY

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.should_run:
            try:
                with self.get_connection() as connection:
                    metrics = self.check_health(connection)
                    
                    with self.lock:
                        # Add to history
                        self.metrics_history.append((datetime.now(), metrics))
                        
                        # Trim history
                        if len(self.metrics_history) > self.history_size:
                            self.metrics_history = self.metrics_history[-self.history_size:]
                        
                        # Check for alerts
                        self._check_alerts(metrics)
                    
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
            
            time.sleep(self.check_interval)

    def _check_alerts(self, metrics: HealthMetrics) -> None:
        """Checks metrics against thresholds and triggers alerts."""
        alerts = []
        
        # Check response time
        if metrics.response_time_ms > self.thresholds['response_time_ms']['critical']:
            alerts.append(('CRITICAL', f"Response time critical: {metrics.response_time_ms}ms"))
        elif metrics.response_time_ms > self.thresholds['response_time_ms']['warning']:
            alerts.append(('WARNING', f"Response time high: {metrics.response_time_ms}ms"))
        
        # Check resource usage
        if metrics.cpu_usage > self.thresholds['cpu_usage']['critical']:
            alerts.append(('CRITICAL', f"CPU usage critical: {metrics.cpu_usage}%"))
        elif metrics.cpu_usage > self.thresholds['cpu_usage']['warning']:
            alerts.append(('WARNING', f"CPU usage high: {metrics.cpu_usage}%"))
        
        # Trigger alert handlers
        for alert_type, message in alerts:
            for handler in self.alert_handlers:
                try:
                    handler(alert_type, message, metrics)
                except Exception as e:
                    self.logger.error(f"Alert handler error: {str(e)}")

    def get_metrics_summary(self, 
                          time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Gets summary of health metrics.
        
        Args:
            time_range: Optional time range to summarize
            
        Returns:
            Dictionary of summarized metrics
            
        Example:
            summary = monitor.get_metrics_summary(timedelta(hours=1))
            print(f"Average response time: {summary['avg_response_time']}ms")
        """
        with self.lock:
            if not self.metrics_history:
                return {"status": "No metrics available"}
            
            # Filter metrics by time range
            if time_range:
                cutoff = datetime.now() - time_range
                metrics = [m for t, m in self.metrics_history if t >= cutoff]
            else:
                metrics = [m for _, m in self.metrics_history]
            
            if not metrics:
                return {"status": "No metrics in specified time range"}
            
            # Calculate statistics
            return {
                "current_status": metrics[-1].status.value,
                "avg_response_time": sum(m.response_time_ms for m in metrics) / len(metrics),
                "max_response_time": max(m.response_time_ms for m in metrics),
                "avg_connection_count": sum(m.connection_count for m in metrics) / len(metrics),
                "max_connection_count": max(m.connection_count for m in metrics),
                "avg_cpu_usage": sum(m.cpu_usage for m in metrics) / len(metrics),
                "max_cpu_usage": max(m.cpu_usage for m in metrics),
                "avg_memory_usage": sum(m.memory_usage for m in metrics) / len(metrics),
                "max_memory_usage": max(m.memory_usage for m in metrics),
                "total_errors": sum(m.error_count for m in metrics),
                "total_warnings": sum(m.warning_count for m in metrics),
                "metrics_count": len(metrics)
            }

    def export_metrics(self, 
                      format: str = 'json',
                      file_path: Optional[str] = None) -> Optional[str]:
        """
        Exports metrics history.
        
        Args:
            format: Export format ('json' or 'csv')
            file_path: Optional file path to save metrics
            
        Returns:
            Exported metrics string if no file_path provided
            
        Example:
            # Export to file
            monitor.export_metrics('json', 'metrics.json')
            
            # Get metrics string
            metrics_json = monitor.export_metrics('json')
        """
        with self.lock:
            if format == 'json':
                export_data = [
                    {
                        'timestamp': t.isoformat(),
                        'status': m.status.value,
                        'response_time_ms': m.response_time_ms,
                        'connection_count': m.connection_count,
                        'cpu_usage': m.cpu_usage,
                        'memory_usage': m.memory_usage,
                        'disk_usage': m.disk_usage,
                        'error_count': m.error_count,
                        'warning_count': m.warning_count
                    }
                    for t, m in self.metrics_history
                ]
                
                output = json.dumps(export_data, indent=2)
                
            elif format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'timestamp', 'status', 'response_time_ms', 'connection_count',
                    'cpu_usage', 'memory_usage', 'disk_usage', 'error_count',
                    'warning_count'
                ])
                
                # Write data
                for t, m in self.metrics_history:
                    writer.writerow([
                        t.isoformat(), m.status.value, m.response_time_ms,
                        m.connection_count, m.cpu_usage, m.memory_usage,
                        m.disk_usage, m.error_count, m.warning_count
                    ])
                
                output = output.getvalue()
                
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(output)
                return None
            
            return output
```

[🔝 Back to Table of Contents](#table-of-contents)

### Database Security and Encryption Patterns

#### 1. Database Security Manager
```python
from typing import Optional, Dict, List, Any, Union
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import dataclass
import logging
import json
from enum import Enum
import threading
import re

class SecurityLevel(Enum):
    """Database security level indicators."""
    HIGH = "HIGH"          # Encryption + Advanced security features
    MEDIUM = "MEDIUM"      # Basic encryption + Standard security
    BASIC = "BASIC"        # Minimal security features
    CUSTOM = "CUSTOM"      # Custom security configuration

@dataclass
class SecurityConfig:
    """Database security configuration."""
    level: SecurityLevel
    encryption_enabled: bool = True
    key_rotation_days: int = 90
    password_policy: Dict[str, Any] = None
    audit_logging: bool = True
    ip_whitelist: List[str] = None
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    sensitive_columns: Dict[str, List[str]] = None

class DatabaseSecurityManager:
    """Manages database security, encryption, and access control."""
    
    def __init__(self, 
                 security_config: SecurityConfig,
                 key_storage_path: Optional[str] = None):
        """
        Initialize security manager.
        
        Args:
            security_config: Security configuration
            key_storage_path: Path for storing encryption keys
        """
        self.config = security_config
        self.key_storage_path = key_storage_path or os.path.expanduser('~/.db_keys')
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Initialize security components
        self._init_security_components()
        self._failed_attempts: Dict[str, List[datetime]] = {}
        self._locked_accounts: Dict[str, datetime] = {}
        
        # Default password policy
        self.default_password_policy = {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special': True,
            'max_age_days': 90,
            'history_size': 5
        }
        
        if not self.config.password_policy:
            self.config.password_policy = self.default_password_policy

    def _init_security_components(self) -> None:
        """Initializes security components based on configuration."""
        os.makedirs(self.key_storage_path, mode=0o700, exist_ok=True)
        
        if self.config.encryption_enabled:
            self._init_encryption()
        
        if self.config.audit_logging:
            self._init_audit_logging()
        
        # Initialize IP whitelist
        if self.config.ip_whitelist:
            self._compile_ip_patterns()

    def _init_encryption(self) -> None:
        """Initializes encryption components."""
        self.key_file = os.path.join(self.key_storage_path, 'encryption.key')
        
        if not os.path.exists(self.key_file):
            self._generate_new_key()
        else:
            self._load_encryption_key()
        
        # Check key rotation
        self._check_key_rotation()

    def _generate_new_key(self) -> None:
        """Generates new encryption key."""
        key = Fernet.generate_key()
        
        with open(self.key_file, 'wb') as f:
            f.write(key)
        
        self.cipher_suite = Fernet(key)
        self.key_generation_time = datetime.now()

    def _load_encryption_key(self) -> None:
        """Loads existing encryption key."""
        with open(self.key_file, 'rb') as f:
            key = f.read()
        
        self.cipher_suite = Fernet(key)
        self.key_generation_time = datetime.fromtimestamp(
            os.path.getctime(self.key_file)
        )

    def _check_key_rotation(self) -> None:
        """Checks if key rotation is needed."""
        if (datetime.now() - self.key_generation_time).days >= self.config.key_rotation_days:
            self._rotate_encryption_key()

    def _rotate_encryption_key(self) -> None:
        """Rotates encryption key."""
        old_key = self.cipher_suite
        self._generate_new_key()
        
        # Re-encrypt sensitive data with new key
        self._reencrypt_sensitive_data(old_key)

    def _reencrypt_sensitive_data(self, old_key: Fernet) -> None:
        """Re-encrypts sensitive data with new key."""
        if not self.config.sensitive_columns:
            return
            
        for table, columns in self.config.sensitive_columns.items():
            self._reencrypt_table_data(table, columns, old_key)

    def _reencrypt_table_data(self, 
                             table: str, 
                             columns: List[str],
                             old_key: Fernet) -> None:
        """Re-encrypts data in specific table columns."""
        query = f"""
            SELECT id, {', '.join(columns)}
            FROM {table}
        """
        
        update_query = f"""
            UPDATE {table}
            SET {', '.join(f'{col} = ?' for col in columns)}
            WHERE id = ?
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                
                for row in rows:
                    id_val = row[0]
                    encrypted_values = []
                    
                    for value in row[1:]:
                        if value:
                            # Decrypt with old key and re-encrypt with new key
                            decrypted = old_key.decrypt(value.encode())
                            encrypted = self.cipher_suite.encrypt(decrypted)
                            encrypted_values.append(encrypted.decode())
                        else:
                            encrypted_values.append(None)
                    
                    # Update with new encrypted values
                    cursor.execute(update_query, encrypted_values + [id_val])
            
            conn.commit()

    def encrypt_value(self, value: str) -> str:
        """
        Encrypts a single value.
        
        Args:
            value: Value to encrypt
            
        Returns:
            Encrypted value
            
        Example:
            encrypted = security_manager.encrypt_value("sensitive data")
        """
        if not self.config.encryption_enabled:
            return value
            
        return self.cipher_suite.encrypt(value.encode()).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """
        Decrypts a single value.
        
        Args:
            encrypted_value: Value to decrypt
            
        Returns:
            Decrypted value
            
        Example:
            decrypted = security_manager.decrypt_value(encrypted_value)
        """
        if not self.config.encryption_enabled:
            return encrypted_value
            
        return self.cipher_suite.decrypt(encrypted_value.encode()).decode()

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validates password against policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            valid, message = security_manager.validate_password("MyP@ssw0rd")
            if not valid:
                print(f"Password invalid: {message}")
        """
        policy = self.config.password_policy
        
        if len(password) < policy['min_length']:
            return False, f"Password must be at least {policy['min_length']} characters"
        
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letters"
            
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            return False, "Password must contain lowercase letters"
            
        if policy['require_numbers'] and not any(c.isdigit() for c in password):
            return False, "Password must contain numbers"
            
        if policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special characters"
            
        return True, "Password meets policy requirements"

    def check_access(self, 
                    username: str,
                    ip_address: str) -> Tuple[bool, str]:
        """
        Checks access permissions.
        
        Args:
            username: Username attempting access
            ip_address: IP address of request
            
        Returns:
            Tuple of (is_allowed, message)
            
        Example:
            allowed, message = security_manager.check_access(
                "user123", 
                "192.168.1.100"
            )
        """
        # Check IP whitelist
        if self.config.ip_whitelist and not self._is_ip_allowed(ip_address):
            return False, "IP address not allowed"
        
        # Check account lockout
        if username in self._locked_accounts:
            lockout_time = self._locked_accounts[username]
            if datetime.now() < lockout_time:
                return False, "Account is locked"
            else:
                del self._locked_accounts[username]
        
        return True, "Access allowed"

    def _is_ip_allowed(self, ip_address: str) -> bool:
        """Checks if IP address is allowed."""
        return any(
            pattern.match(ip_address)
            for pattern in self._ip_patterns
        )

    def _compile_ip_patterns(self) -> None:
        """Compiles IP whitelist patterns."""
        self._ip_patterns = []
        for ip in self.config.ip_whitelist:
            # Convert wildcards to regex pattern
            pattern = ip.replace('.', '\\.').replace('*', '.*')
            self._ip_patterns.append(re.compile(f"^{pattern}$"))

    def record_failed_attempt(self, username: str) -> None:
        """
        Records failed login attempt.
        
        Args:
            username: Username that failed login
            
        Example:
            security_manager.record_failed_attempt("user123")
        """
        now = datetime.now()
        
        if username not in self._failed_attempts:
            self._failed_attempts[username] = []
        
        self._failed_attempts[username].append(now)
        
        # Remove old attempts
        cutoff = now - timedelta(minutes=self.config.lockout_duration_minutes)
        self._failed_attempts[username] = [
            attempt for attempt in self._failed_attempts[username]
            if attempt > cutoff
        ]
        
        # Check if account should be locked
        if len(self._failed_attempts[username]) >= self.config.max_failed_attempts:
            self._locked_accounts[username] = now + timedelta(
                minutes=self.config.lockout_duration_minutes
            )

    def audit_log(self, 
                  event_type: str,
                  username: str,
                  details: Dict[str, Any]) -> None:
        """
        Logs security audit event.
        
        Args:
            event_type: Type of event
            username: Username involved
            details: Event details
            
        Example:
            security_manager.audit_log(
                "LOGIN_ATTEMPT",
                "user123",
                {
                    "ip_address": "192.168.1.100",
                    "success": False,
                    "reason": "Invalid password"
                }
            )
        """
        if not self.config.audit_logging:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "username": username,
            "details": details
        }
        
        self.logger.info("Security audit: %s", json.dumps(log_entry))

    def get_security_status(self) -> Dict[str, Any]:
        """
        Gets current security status.
        
        Returns:
            Dictionary of security status information
            
        Example:
            status = security_manager.get_security_status()
            print(f"Security Level: {status['security_level']}")
        """
        return {
            "security_level": self.config.level.value,
            "encryption_enabled": self.config.encryption_enabled,
            "key_age_days": (datetime.now() - self.key_generation_time).days,
            "locked_accounts": list(self._locked_accounts.keys()),
            "ip_whitelist_enabled": bool(self.config.ip_whitelist),
            "audit_logging_enabled": self.config.audit_logging,
            "password_policy": self.config.password_policy
        }
```

[🔝 Back to Table of Contents](#table-of-contents)

from typing import Optional, Dict, List, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import queue
import hashlib
import json
import logging
from enum import Enum
import copy

class SyncStrategy(Enum):
    """Synchronization strategy types."""
    FULL_SYNC = "FULL"           # Complete table synchronization
    INCREMENTAL = "INCREMENTAL"  # Changes since last sync
    SNAPSHOT = "SNAPSHOT"        # Point-in-time copy
    MERGE = "MERGE"              # Merge changes with conflict resolution

@dataclass
class SyncConfig:
    """Configuration for synchronization."""
    source_table: str
    target_table: str
    key_columns: List[str]
    columns_to_sync: List[str]
    track_changes: bool = True
    batch_size: int = 1000
    conflict_resolution: str = "SOURCE_WINS"  # SOURCE_WINS, TARGET_WINS, MANUAL
    transform_function: Optional[callable] = None
    validation_query: Optional[str] = None

class DatabaseSynchronizer:
    """Manages cross-database synchronization operations."""
    
    def __init__(self, 
                 source_connector: Any,
                 target_connector: Any,
                 sync_configs: List[SyncConfig]):
        """
        Initialize synchronizer.
        
        Args:
            source_connector: Source database connector
            target_connector: Target database connector
            sync_configs: List of synchronization configurations
            
        Example:
            sync_config = SyncConfig(
                source_table="users",
                target_table="users_replica",
                key_columns=["id"],
                columns_to_sync=["name", "email", "updated_at"]
            )
            
            synchronizer = DatabaseSynchronizer(
                source_db,
                target_db,
                [sync_config]
            )
        """
        self.source = source_connector
        self.target = target_connector
        self.configs = {config.source_table: config for config in sync_configs}
        
        self.logger = logging.getLogger(__name__)
        self._sync_queue = queue.Queue()
        self._sync_thread = None
        self._should_run = False
        
        # Initialize change tracking tables
        self._init_change_tracking()

    def _init_change_tracking(self) -> None:
        """Initializes change tracking infrastructure."""
        tracking_table_sql = """
            CREATE TABLE IF NOT EXISTS sync_tracking (
                table_name VARCHAR(255),
                record_key VARCHAR(255),
                change_type VARCHAR(10),
                changed_at TIMESTAMP,
                checksum VARCHAR(64),
                is_synced BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (table_name, record_key)
            )
        """
        
        with self.source.transaction() as conn:
            conn.execute(tracking_table_sql)
        
        with self.target.transaction() as conn:
            conn.execute(tracking_table_sql)

    def start_sync_worker(self) -> None:
        """
        Starts background synchronization worker.
        
        Example:
            synchronizer.start_sync_worker()
        """
        if self._sync_thread is not None:
            return
            
        self._should_run = True
        self._sync_thread = threading.Thread(
            target=self._sync_worker,
            daemon=True
        )
        self._sync_thread.start()

    def stop_sync_worker(self) -> None:
        """
        Stops background synchronization worker.
        
        Example:
            synchronizer.stop_sync_worker()
        """
        self._should_run = False
        if self._sync_thread:
            self._sync_thread.join()
            self._sync_thread = None

    def _sync_worker(self) -> None:
        """Background worker for processing sync queue."""
        while self._should_run:
            try:
                sync_task = self._sync_queue.get(timeout=1)
                self._process_sync_task(sync_task)
                self._sync_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Sync worker error: {str(e)}")

    def sync_table(self, 
                  table_name: str,
                  strategy: SyncStrategy = SyncStrategy.INCREMENTAL) -> Dict[str, Any]:
        """
        Synchronizes a table between databases.
        
        Args:
            table_name: Name of table to synchronize
            strategy: Synchronization strategy to use
            
        Returns:
            Dictionary with synchronization results
            
        Example:
            results = synchronizer.sync_table(
                "users",
                strategy=SyncStrategy.INCREMENTAL
            )
            print(f"Synced {results['rows_synced']} rows")
        """
        if table_name not in self.configs:
            raise ValueError(f"No sync configuration for table: {table_name}")
            
        config = self.configs[table_name]
        results = {
            "table_name": table_name,
            "strategy": strategy.value,
            "started_at": datetime.now(),
            "rows_synced": 0,
            "conflicts": 0,
            "errors": 0
        }
        
        try:
            if strategy == SyncStrategy.FULL_SYNC:
                results.update(self._full_sync(config))
            elif strategy == SyncStrategy.INCREMENTAL:
                results.update(self._incremental_sync(config))
            elif strategy == SyncStrategy.SNAPSHOT:
                results.update(self._snapshot_sync(config))
            elif strategy == SyncStrategy.MERGE:
                results.update(self._merge_sync(config))
                
        except Exception as e:
            results["status"] = "ERROR"
            results["error_message"] = str(e)
            self.logger.error(f"Sync error for {table_name}: {str(e)}")
            raise
            
        finally:
            results["completed_at"] = datetime.now()
            results["duration_seconds"] = (
                results["completed_at"] - results["started_at"]
            ).total_seconds()
            
        return results

    def _full_sync(self, config: SyncConfig) -> Dict[str, Any]:
        """Performs full table synchronization."""
        results = {"status": "SUCCESS", "rows_synced": 0}
        
        # Get all source records
        source_records = self._get_source_records(config)
        
        # Clear target table
        self._clear_target_table(config)
        
        # Copy records in batches
        for batch in self._batch_records(source_records, config.batch_size):
            transformed_batch = self._transform_batch(batch, config)
            self._write_batch_to_target(transformed_batch, config)
            results["rows_synced"] += len(batch)
        
        return results

    def _incremental_sync(self, config: SyncConfig) -> Dict[str, Any]:
        """Performs incremental synchronization."""
        results = {"status": "SUCCESS", "rows_synced": 0, "changes_detected": 0}
        
        # Get changed records
        changes = self._get_changed_records(config)
        results["changes_detected"] = len(changes)
        
        # Process changes in batches
        for batch in self._batch_records(changes, config.batch_size):
            synced = self._sync_changes_batch(batch, config)
            results["rows_synced"] += synced
        
        return results

    def _snapshot_sync(self, config: SyncConfig) -> Dict[str, Any]:
        """Creates point-in-time snapshot."""
        results = {"status": "SUCCESS", "rows_synced": 0}
        
        # Create snapshot table name
        snapshot_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_table = f"{config.target_table}_snapshot_{snapshot_time}"
        
        # Copy structure
        self._copy_table_structure(
            config.source_table,
            snapshot_table,
            self.source,
            self.target
        )
        
        # Copy data
        source_records = self._get_source_records(config)
        for batch in self._batch_records(source_records, config.batch_size):
            transformed_batch = self._transform_batch(batch, config)
            self._write_batch_to_target(
                transformed_batch,
                config,
                target_table=snapshot_table
            )
            results["rows_synced"] += len(batch)
        
        results["snapshot_table"] = snapshot_table
        return results

    def _merge_sync(self, config: SyncConfig) -> Dict[str, Any]:
        """Performs merge synchronization with conflict resolution."""
        results = {
            "status": "SUCCESS",
            "rows_synced": 0,
            "conflicts": 0,
            "resolved_conflicts": 0
        }
        
        # Get changes from both sides
        source_changes = self._get_changed_records(config, source=True)
        target_changes = self._get_changed_records(config, source=False)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(source_changes, target_changes, config)
        results["conflicts"] = len(conflicts)
        
        # Resolve conflicts
        resolved_changes = self._resolve_conflicts(conflicts, config)
        results["resolved_conflicts"] = len(resolved_changes)
        
        # Apply resolved changes
        for batch in self._batch_records(resolved_changes, config.batch_size):
            synced = self._sync_changes_batch(batch, config)
            results["rows_synced"] += synced
        
        return results

    def _get_source_records(self, 
                           config: SyncConfig,
                           where_clause: Optional[str] = None) -> List[Dict[str, Any]]:
        """Gets records from source database."""
        columns = ", ".join(config.columns_to_sync + config.key_columns)
        query = f"SELECT {columns} FROM {config.source_table}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        with self.source.transaction() as conn:
            return conn.execute(query).fetchall()

    def _get_changed_records(self, 
                           config: SyncConfig,
                           source: bool = True) -> List[Dict[str, Any]]:
        """Gets changed records from tracking table."""
        db = self.source if source else self.target
        
        query = f"""
            SELECT t.*, c.change_type
            FROM {config.source_table} t
            JOIN sync_tracking c ON t.{config.key_columns[0]} = c.record_key
            WHERE c.table_name = ? AND c.is_synced = FALSE
        """
        
        with db.transaction() as conn:
            return conn.execute(query, [config.source_table]).fetchall()

    def _transform_batch(self, 
                        batch: List[Dict[str, Any]],
                        config: SyncConfig) -> List[Dict[str, Any]]:
        """Applies transformation to batch of records."""
        if not config.transform_function:
            return batch
            
        return [config.transform_function(record) for record in batch]

    def _write_batch_to_target(self,
                              batch: List[Dict[str, Any]],
                              config: SyncConfig,
                              target_table: Optional[str] = None) -> None:
        """Writes batch of records to target database."""
        if not batch:
            return
            
        table = target_table or config.target_table
        columns = config.columns_to_sync + config.key_columns
        placeholders = ",".join(["?"] * len(columns))
        
        insert_sql = f"""
            INSERT INTO {table} ({",".join(columns)})
            VALUES ({placeholders})
        """
        
        with self.target.transaction() as conn:
            conn.executemany(
                insert_sql,
                [[record[col] for col in columns] for record in batch]
            )

    def _detect_conflicts(self,
                         source_changes: List[Dict[str, Any]],
                         target_changes: List[Dict[str, Any]],
                         config: SyncConfig) -> List[Dict[str, Any]]:
        """Detects conflicts between source and target changes."""
        conflicts = []
        source_keys = {
            self._get_key(record, config.key_columns): record
            for record in source_changes
        }
        target_keys = {
            self._get_key(record, config.key_columns): record
            for record in target_changes
        }
        
        # Find records changed in both sources
        for key in set(source_keys) & set(target_keys):
            source_record = source_keys[key]
            target_record = target_keys[key]
            
            if self._records_differ(source_record, target_record, config):
                conflicts.append({
                    "key": key,
                    "source_record": source_record,
                    "target_record": target_record
                })
        
        return conflicts

    def _resolve_conflicts(self,
                          conflicts: List[Dict[str, Any]],
                          config: SyncConfig) -> List[Dict[str, Any]]:
        """Resolves conflicts based on configuration."""
        resolved = []
        
        for conflict in conflicts:
            if config.conflict_resolution == "SOURCE_WINS":
                resolved.append(conflict["source_record"])
            elif config.conflict_resolution == "TARGET_WINS":
                resolved.append(conflict["target_record"])
            elif config.conflict_resolution == "MANUAL":
                # Log conflict for manual resolution
                self.logger.warning(
                    f"Manual conflict resolution required for {config.source_table} "
                    f"key: {conflict['key']}"
                )
        
        return resolved

    def _get_key(self, record: Dict[str, Any], key_columns: List[str]) -> str:
        """Generates composite key from record."""
        return "|".join(str(record[col]) for col in key_columns)

    def _records_differ(self,
                       record1: Dict[str, Any],
                       record2: Dict[str, Any],
                       config: SyncConfig) -> bool:
        """Checks if records have different values in synced columns."""
        return any(
            record1[col] != record2[col]
            for col in config.columns_to_sync
        )

    def validate_sync(self, table_name: str) -> Dict[str, Any]:
        """
        Validates synchronization results.
        
        Args:
            table_name: Name of table to validate
            
        Returns:
            Dictionary with validation results
            
        Example:
            results = synchronizer.validate_sync("users")
            if not results["is_valid"]:
                print(f"Validation failed: {results['errors']}")
        """
        if table_name not in self.configs:
            raise ValueError(f"No sync configuration for table: {table_name}")
            
        config = self.configs[table_name]
        results = {
            "table_name": table_name,
            "started_at": datetime.now(),
            "is_valid": True,
            "errors": []
        }
        
        try:
            # Run custom validation query if provided
            if config.validation_query:
                self._run_validation_query(config.validation_query, results)
            
            # Compare record counts
            source_count = self._get_record_count(config.source_table, self.source)
            target_count = self._get_record_count(config.target_table, self.target)
            
            if source_count != target_count:
                results["is_valid"] = False
                results["errors"].append(
                    f"Record count mismatch: source={source_count}, target={target_count}"
                )
            
            # Compare data checksums
            if results["is_valid"]:
                source_checksum = self._calculate_table_checksum(
                    config.source_table,
                    config.columns_to_sync,
                    self.source
                )
                target_checksum = self._calculate_table_checksum(
                    config.target_table,
                    config.columns_to_sync,
                    self.target
                )
                
                if source_checksum != target_checksum:
                    results["is_valid"] = False
                    results["errors"].append("Data checksum mismatch")
            
            results["source_count"] = source_count
            results["target_count"] = target_count
            
        except Exception as e:
            results["is_valid"] = False
            results["errors"].append(str(e))
            
        finally:
            results["completed_at"] = datetime.now()
            results["duration_seconds"] = (
                results["completed_at"] - results["started_at"]
            ).total_seconds()
        
        return results

    def _run_validation_query(self, query: str, results: Dict[str, Any]) -> None:
        """Runs custom validation query."""
        try:
            source_result = self.source.execute_query(query)
            target_result = self.target.execute_query(query)
            
            if source_result != target_result:
                results["is_valid"] = False
                results["errors"].append(
                    "Custom validation query results mismatch"
                )
                results["validation_details"] = {
                    "source_result": source_result,
                    "target_result": target_result
                }
        except Exception as e:
            results["is_valid"] = False
            results["errors"].append(f"Validation query error: {str(e)}")

    def _calculate_table_checksum(self,
                                table_name: str,
                                columns: List[str],
                                connection: Any) -> str:
        """Calculates checksum for table data."""
        columns_concat = "||'|'||".join(columns)
        query = f"""
            SELECT GROUP_CONCAT(CAST(hash AS TEXT))
            FROM (
                SELECT MD5({columns_concat}) as hash
                FROM {table_name}
                ORDER BY {columns_concat}
            )
        """
        
        with connection.transaction() as conn:
            result = conn.execute(query).fetchone()[0]
            return hashlib.md5(result.encode()).hexdigest()

    def get_sync_status(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Gets synchronization status information.
        
        Args:
            table_name: Optional specific table name
            
        Returns:
            Dictionary with sync status information
            
        Example:
            status = synchronizer.get_sync_status("users")
            print(f"Last sync: {status['last_sync_time']}")
        """
        if table_name and table_name not in self.configs:
            raise ValueError(f"No sync configuration for table: {table_name}")
        
        query = """
            SELECT table_name,
                   COUNT(*) as pending_changes,
                   MAX(changed_at) as last_change
            FROM sync_tracking
            WHERE is_synced = FALSE
        """
        
        if table_name:
            query += f" AND table_name = '{table_name}'"
        
        query += " GROUP BY table_name"
        
        with self.source.transaction() as conn:
            results = conn.execute(query).fetchall()
        
        status = {
            "sync_queue_size": self._sync_queue.qsize(),
            "worker_active": self._sync_thread is not None and self._sync_thread.is_alive(),
            "tables": {}
        }
        
        for result in results:
            status["tables"][result["table_name"]] = {
                "pending_changes": result["pending_changes"],
                "last_change": result["last_change"].isoformat() if result["last_change"] else None
            }
        
        return status

#### 2. Cross-Database Query Builder
```python
class CrossDatabaseQueryBuilder:
    """Builds and executes queries across multiple databases."""
    
    def __init__(self, database_connections: Dict[str, Any]):
        """
        Initialize query builder.
        
        Args:
            database_connections: Dictionary of database connections
            
        Example:
            connections = {
                "sales_db": sales_connection,
                "customer_db": customer_connection
            }
            query_builder = CrossDatabaseQueryBuilder(connections)
        """
        self.connections = database_connections
        self.logger = logging.getLogger(__name__)

    def execute_distributed_query(self, 
                                query_parts: Dict[str, str],
                                join_keys: Dict[str, str]) -> pd.DataFrame:
        """
        Executes distributed query across databases.
        
        Args:
            query_parts: Dictionary of database-specific queries
            join_keys: Dictionary of join keys for each database
            
        Returns:
            DataFrame with combined results
            
        Example:
            results = query_builder.execute_distributed_query(
                {
                    "sales_db": "SELECT order_id, customer_id, amount FROM orders",
                    "customer_db": "SELECT customer_id, name, email FROM customers"
                },
                {
                    "sales_db": "customer_id",
                    "customer_db": "customer_id"
                }
            )
        """
        # Execute individual queries
        results = {}
        for db_name, query in query_parts.items():
            if db_name not in self.connections:
                raise ValueError(f"Unknown database: {db_name}")
                
            connection = self.connections[db_name]
            results[db_name] = pd.read_sql(query, connection)
        
        # Combine results
        combined_df = None
        for db_name, df in results.items():
            if combined_df is None:
                combined_df = df
            else:
                join_key = join_keys[db_name]
                combined_df = combined_df.merge(
                    df,
                    on=join_key,
                    how='inner'
                )
        
        return combined_df

    def execute_federated_query(self,
                              template_query: str,
                              parameter_sets: Dict[str, List[Any]]) -> pd.DataFrame:
        """
        Executes same query across multiple databases.
        
        Args:
            template_query: Query template to execute
            parameter_sets: Parameters for each database
            
        Returns:
            DataFrame with combined results
            
        Example:
            results = query_builder.execute_federated_query(
                "SELECT * FROM users WHERE region = ?",
                {
                    "db1": ["NA"],
                    "db2": ["EU"]
                }
            )
        """
        results = []
        
        for db_name, params in parameter_sets.items():
            if db_name not in self.connections:
                raise ValueError(f"Unknown database: {db_name}")
                
            connection = self.connections[db_name]
            df = pd.read_sql(template_query, connection, params=params)
            df['source_database'] = db_name
            results.append(df)
        
        return pd.concat(results, ignore_index=True)

from typing import Optional, Dict, List, Any, Callable, Union
from dataclasses import dataclass
import unittest
from datetime import datetime
import json
import logging
from enum import Enum
import copy
import pytest

@dataclass
class TestCase:
    """Database test case configuration."""
    name: str
    description: str
    setup_queries: List[str]
    test_queries: List[str]
    expected_results: List[Any]
    cleanup_queries: List[str]
    validation_func: Optional[Callable] = None
    timeout: int = 30

class TestResult(Enum):
    """Test execution result status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"

class DatabaseTestSuite:
    """Comprehensive database testing framework."""
    
    def __init__(self, connection: Any, test_cases: List[TestCase]):
        """
        Initialize test suite.
        
        Args:
            connection: Database connection
            test_cases: List of test cases to execute
            
        Example:
            test_case = TestCase(
                name="Insert User Test",
                description="Tests user insertion functionality",
                setup_queries=["CREATE TABLE test_users (id INT, name TEXT)"],
                test_queries=["INSERT INTO test_users VALUES (1, 'Test User')"],
                expected_results=[1],
                cleanup_queries=["DROP TABLE test_users"]
            )
            
            test_suite = DatabaseTestSuite(connection, [test_case])
        """
        self.connection = connection
        self.test_cases = test_cases
        self.logger = logging.getLogger(__name__)
        self.results: Dict[str, Dict[str, Any]] = {}

    def run_tests(self, 
                  parallel: bool = False,
                  stop_on_failure: bool = False) -> Dict[str, Any]:
        """
        Executes all test cases.
        
        Args:
            parallel: Whether to run tests in parallel
            stop_on_failure: Whether to stop on first failure
            
        Returns:
            Dictionary with test results
            
        Example:
            results = test_suite.run_tests(parallel=True)
            print(f"Passed: {results['passed_count']}")
        """
        start_time = datetime.now()
        summary = {
            "total_tests": len(self.test_cases),
            "passed_count": 0,
            "failed_count": 0,
            "error_count": 0,
            "skipped_count": 0
        }
        
        if parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._run_test_case, test_case): test_case.name
                    for test_case in self.test_cases
                }
                
                for future in concurrent.futures.as_completed(futures):
                    test_name = futures[future]
                    try:
                        result = future.result()
                        self._update_summary(summary, result["status"])
                        self.results[test_name] = result
                        
                        if stop_on_failure and result["status"] == TestResult.FAILED:
                            break
                    except Exception as e:
                        self.logger.error(f"Test execution error: {str(e)}")
                        summary["error_count"] += 1
        else:
            for test_case in self.test_cases:
                result = self._run_test_case(test_case)
                self._update_summary(summary, result["status"])
                self.results[test_case.name] = result
                
                if stop_on_failure and result["status"] == TestResult.FAILED:
                    break
        
        summary["duration_seconds"] = (datetime.now() - start_time).total_seconds()
        summary["results"] = self.results
        return summary

    def _run_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Executes single test case."""
        result = {
            "name": test_case.name,
            "description": test_case.description,
            "started_at": datetime.now(),
            "status": TestResult.PASSED,
            "error_message": None
        }
        
        try:
            # Setup phase
            self._execute_setup(test_case)
            
            # Test execution phase
            test_results = []
            for query in test_case.test_queries:
                test_results.append(
                    self._execute_query(query)
                )
            
            # Validation phase
            if test_case.validation_func:
                is_valid = test_case.validation_func(test_results)
            else:
                is_valid = self._validate_results(
                    test_results,
                    test_case.expected_results
                )
            
            if not is_valid:
                result["status"] = TestResult.FAILED
                result["error_message"] = "Results validation failed"
                result["actual_results"] = test_results
                result["expected_results"] = test_case.expected_results
            
        except Exception as e:
            result["status"] = TestResult.ERROR
            result["error_message"] = str(e)
            self.logger.error(f"Test case error: {str(e)}")
            
        finally:
            # Cleanup phase
            try:
                self._execute_cleanup(test_case)
            except Exception as e:
                self.logger.error(f"Cleanup error: {str(e)}")
            
            result["completed_at"] = datetime.now()
            result["duration_seconds"] = (
                result["completed_at"] - result["started_at"]
            ).total_seconds()
        
        return result

    def _execute_setup(self, test_case: TestCase) -> None:
        """Executes test case setup."""
        for query in test_case.setup_queries:
            self._execute_query(query)

    def _execute_cleanup(self, test_case: TestCase) -> None:
        """Executes test case cleanup."""
        for query in test_case.cleanup_queries:
            self._execute_query(query)

    def _execute_query(self, query: str) -> Any:
        """Executes single query with error handling."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                try:
                    return cursor.fetchall()
                except:
                    return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Query execution error: {str(e)}")
            raise

    def _validate_results(self,
                         actual_results: List[Any],
                         expected_results: List[Any]) -> bool:
        """Validates test results against expected values."""
        if len(actual_results) != len(expected_results):
            return False
            
        return all(
            self._compare_results(actual, expected)
            for actual, expected in zip(actual_results, expected_results)
        )

    def _compare_results(self,
                        actual: Any,
                        expected: Any) -> bool:
        """Compares individual test results."""
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            return len(actual) == len(expected) and all(
                self._compare_results(a, e)
                for a, e in zip(actual, expected)
            )
        elif isinstance(actual, dict) and isinstance(expected, dict):
            return actual.keys() == expected.keys() and all(
                self._compare_results(actual[k], expected[k])
                for k in actual.keys()
            )
        else:
            return actual == expected

    def _update_summary(self,
                       summary: Dict[str, int],
                       status: TestResult) -> None:
        """Updates test summary statistics."""
        if status == TestResult.PASSED:
            summary["passed_count"] += 1
        elif status == TestResult.FAILED:
            summary["failed_count"] += 1
        elif status == TestResult.ERROR:
            summary["error_count"] += 1
        elif status == TestResult.SKIPPED:
            summary["skipped_count"] += 1

    def generate_report(self,
                       format: str = 'text',
                       file_path: Optional[str] = None) -> Optional[str]:
        """
        Generates test execution report.
        
        Args:
            format: Report format ('text', 'json', 'html')
            file_path: Optional file path to save report
            
        Returns:
            Report content if no file_path provided
            
        Example:
            # Generate text report
            report = test_suite.generate_report('text')
            print(report)
            
            # Save HTML report
            test_suite.generate_report('html', 'test_report.html')
        """
        if format == 'text':
            report = self._generate_text_report()
        elif format == 'json':
            report = self._generate_json_report()
        elif format == 'html':
            report = self._generate_html_report()
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(report)
            return None
        
        return report

    def _generate_text_report(self) -> str:
        """Generates text format report."""
        lines = []
        lines.append("Database Test Suite Report")
        lines.append("=" * 30)
        
        # Summary
        passed = sum(1 for r in self.results.values() 
                    if r["status"] == TestResult.PASSED)
        failed = sum(1 for r in self.results.values() 
                    if r["status"] == TestResult.FAILED)
        errors = sum(1 for r in self.results.values() 
                    if r["status"] == TestResult.ERROR)
        
        lines.append(f"Total Tests: {len(self.results)}")
        lines.append(f"Passed: {passed}")
        lines.append(f"Failed: {failed}")
        lines.append(f"Errors: {errors}")
        lines.append("")
        
        # Individual test results
        for name, result in self.results.items():
            lines.append(f"Test: {name}")
            lines.append(f"Status: {result['status'].value}")
            lines.append(f"Duration: {result['duration_seconds']:.2f}s")
            
            if result["error_message"]:
                lines.append(f"Error: {result['error_message']}")
            
            lines.append("-" * 30)
        
        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generates JSON format report."""
        report_data = {
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results.values() 
                            if r["status"] == TestResult.PASSED),
                "failed": sum(1 for r in self.results.values() 
                            if r["status"] == TestResult.FAILED),
                "errors": sum(1 for r in self.results.values() 
                            if r["status"] == TestResult.ERROR)
            },
            "tests": {
                name: {
                    "status": result["status"].value,
                    "duration": result["duration_seconds"],
                    "error": result["error_message"]
                }
                for name, result in self.results.items()
            }
        }
        
        return json.dumps(report_data, indent=2)

    def _generate_html_report(self) -> str:
        """Generates HTML format report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { margin-bottom: 20px; }
                .test { margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; }
                .passed { background-color: #dff0d8; }
                .failed { background-color: #f2dede; }
                .error { background-color: #fcf8e3; }
            </style>
        </head>
        <body>
            <h1>Database Test Suite Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total}</p>
                <p>Passed: {passed}</p>
                <p>Failed: {failed}</p>
                <p>Errors: {errors}</p>
            </div>
            <div class="tests">
                <h2>Test Results</h2>
                {test_results}
            </div>
        </body>
        </html>
        """
        
        test_template = """
        <div class="test {status_class}">
            <h3>{name}</h3>
            <p>Status: {status}</p>
            <p>Duration: {duration:.2f}s</p>
            {error_message}
        </div>
        """
        
        # Generate test result HTML
        test_results = []
        for name, result in self.results.items():
            status = result["status"].value
            status_class = status.lower()
            error_html = (f"<p>Error: {result['error_message']}</p>"
                         if result["error_message"] else "")
            
            test_results.append(
                test_template.format(
                    name=name,
                    status=status,
                    status_class=status_class,
                    duration=result["duration_seconds"],
                    error_message=error_html
                )
            )
        
        # Generate full report
        return html_template.format(
            total=len(self.results),
            passed=sum(1 for r in self.results.values() 
                      if r["status"] == TestResult.PASSED),
            failed=sum(1 for r in self.results.values() 
                      if r["status"] == TestResult.FAILED),
            errors=sum(1 for r in self.results.values() 
                      if r["status"] == TestResult.ERROR),
            test_results="\n".join(test_results)
        )

from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import threading
import queue
from enum import Enum
import os
import shutil

class MaintenanceTaskType(Enum):
    """Types of maintenance tasks."""
    VACUUM = "VACUUM"
    REINDEX = "REINDEX"
    ANALYZE = "ANALYZE"
    BACKUP = "BACKUP"
    CLEANUP = "CLEANUP"
    OPTIMIZE = "OPTIMIZE"
    VALIDATE = "VALIDATE"

@dataclass
class MaintenanceTask:
    """Configuration for maintenance task."""
    task_type: MaintenanceTaskType
    target: str  # table name or database name
    priority: int = 1  # 1 (highest) to 5 (lowest)
    options: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None  # cron-style schedule
    timeout: int = 3600  # seconds
    retry_count: int = 3

class MaintenanceManager:
    """Manages database maintenance and cleanup operations."""
    
    def __init__(self, connection: Any, backup_path: Optional[str] = None):
        """
        Initialize maintenance manager.
        
        Args:
            connection: Database connection
            backup_path: Optional path for backups
            
        Example:
            manager = MaintenanceManager(
                connection,
                backup_path="/path/to/backups"
            )
        """
        self.connection = connection
        self.backup_path = backup_path
        self.logger = logging.getLogger(__name__)
        self.task_queue = queue.PriorityQueue()
        self.maintenance_history: List[Dict[str, Any]] = []
        self._scheduler_thread = None
        self._should_run = False
        
        # Initialize maintenance directories
        if backup_path:
            os.makedirs(backup_path, exist_ok=True)
            os.makedirs(os.path.join(backup_path, 'full'), exist_ok=True)
            os.makedirs(os.path.join(backup_path, 'incremental'), exist_ok=True)

    def schedule_task(self, task: MaintenanceTask) -> None:
        """
        Schedules maintenance task.
        
        Args:
            task: Maintenance task configuration
            
        Example:
            task = MaintenanceTask(
                task_type=MaintenanceTaskType.VACUUM,
                target="large_table",
                priority=2
            )
            manager.schedule_task(task)
        """
        self.task_queue.put((task.priority, datetime.now(), task))
        self.logger.info(
            f"Scheduled {task.task_type.value} task for {task.target}"
        )

    def start_maintenance_scheduler(self) -> None:
        """
        Starts maintenance scheduler thread.
        
        Example:
            manager.start_maintenance_scheduler()
        """
        if self._scheduler_thread is not None:
            return
            
        self._should_run = True
        self._scheduler_thread = threading.Thread(
            target=self._maintenance_scheduler,
            daemon=True
        )
        self._scheduler_thread.start()

    def stop_maintenance_scheduler(self) -> None:
        """
        Stops maintenance scheduler thread.
        
        Example:
            manager.stop_maintenance_scheduler()
        """
        self._should_run = False
        if self._scheduler_thread:
            self._scheduler_thread.join()
            self._scheduler_thread = None

    def _maintenance_scheduler(self) -> None:
        """Main scheduler loop for maintenance tasks."""
        while self._should_run:
            try:
                # Get next task
                if self.task_queue.empty():
                    # Sleep if no tasks
                    time.sleep(60)
                    continue
                
                priority, scheduled_time, task = self.task_queue.get()
                
                # Execute task
                result = self._execute_maintenance_task(task)
                
                # Record result
                self.maintenance_history.append({
                    "task_type": task.task_type.value,
                    "target": task.target,
                    "start_time": result["start_time"],
                    "end_time": result["end_time"],
                    "status": result["status"],
                    "error": result["error"]
                })
                
                # Reschedule if needed
                if task.schedule:
                    next_run = self._calculate_next_run(task.schedule)
                    self.task_queue.put((priority, next_run, task))
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")

    def _execute_maintenance_task(self, task: MaintenanceTask) -> Dict[str, Any]:
        """Executes single maintenance task."""
        result = {
            "start_time": datetime.now(),
            "end_time": None,
            "status": "SUCCESS",
            "error": None
        }
        
        try:
            if task.task_type == MaintenanceTaskType.VACUUM:
                self._execute_vacuum(task)
            elif task.task_type == MaintenanceTaskType.REINDEX:
                self._execute_reindex(task)
            elif task.task_type == MaintenanceTaskType.ANALYZE:
                self._execute_analyze(task)
            elif task.task_type == MaintenanceTaskType.BACKUP:
                self._execute_backup(task)
            elif task.task_type == MaintenanceTaskType.CLEANUP:
                self._execute_cleanup(task)
            elif task.task_type == MaintenanceTaskType.OPTIMIZE:
                self._execute_optimize(task)
            elif task.task_type == MaintenanceTaskType.VALIDATE:
                self._execute_validate(task)
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            self.logger.error(f"Task execution error: {str(e)}")
            
        finally:
            result["end_time"] = datetime.now()
            
        return result

    def _execute_vacuum(self, task: MaintenanceTask) -> None:
        """Executes VACUUM operation."""
        options = task.options or {}
        analyze = options.get('analyze', True)
        full = options.get('full', False)
        
        vacuum_sql = f"VACUUM {'FULL' if full else ''} "
        if analyze:
            vacuum_sql += "ANALYZE "
        vacuum_sql += task.target
        
        with self.connection.cursor() as cursor:
            cursor.execute(vacuum_sql)

    def _execute_reindex(self, task: MaintenanceTask) -> None:
        """Executes REINDEX operation."""
        options = task.options or {}
        concurrent = options.get('concurrent', True)
        
        reindex_sql = f"REINDEX {'CONCURRENTLY' if concurrent else ''} TABLE {task.target}"
        
        with self.connection.cursor() as cursor:
            cursor.execute(reindex_sql)

    def _execute_analyze(self, task: MaintenanceTask) -> None:
        """Executes ANALYZE operation."""
        options = task.options or {}
        verbose = options.get('verbose', False)
        columns = options.get('columns', None)
        
        analyze_sql = f"ANALYZE {'VERBOSE' if verbose else ''} {task.target}"
        if columns:
            analyze_sql += f" ({','.join(columns)})"
        
        with self.connection.cursor() as cursor:
            cursor.execute(analyze_sql)

    def _execute_backup(self, task: MaintenanceTask) -> None:
        """Executes database backup."""
        if not self.backup_path:
            raise ValueError("Backup path not configured")
            
        options = task.options or {}
        backup_type = options.get('type', 'full')
        compress = options.get('compress', True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{task.target}_{timestamp}.backup"
        backup_path = os.path.join(
            self.backup_path,
            backup_type,
            backup_file
        )
        
        # Database-specific backup command
        backup_command = self._get_backup_command(
            task.target,
            backup_path,
            backup_type,
            compress
        )
        
        os.system(backup_command)

    def _execute_cleanup(self, task: MaintenanceTask) -> None:
        """Executes cleanup operations."""
        options = task.options or {}
        cleanup_type = options.get('type', 'old_backups')
        
        if cleanup_type == 'old_backups':
            self._cleanup_old_backups(task)
        elif cleanup_type == 'temp_files':
            self._cleanup_temp_files(task)
        elif cleanup_type == 'dead_rows':
            self._cleanup_dead_rows(task)

    def _execute_optimize(self, task: MaintenanceTask) -> None:
        """Executes database optimization."""
        options = task.options or {}
        optimize_type = options.get('type', 'table')
        
        if optimize_type == 'table':
            self._optimize_table(task)
        elif optimize_type == 'indexes':
            self._optimize_indexes(task)
        elif optimize_type == 'cache':
            self._optimize_cache(task)

    def _execute_validate(self, task: MaintenanceTask) -> None:
        """Executes database validation."""
        options = task.options or {}
        validate_type = options.get('type', 'constraints')
        
        if validate_type == 'constraints':
            self._validate_constraints(task)
        elif validate_type == 'indexes':
            self._validate_indexes(task)
        elif validate_type == 'references':
            self._validate_references(task)

    def _cleanup_old_backups(self, task: MaintenanceTask) -> None:
        """Cleans up old backup files."""
        options = task.options or {}
        retention_days = options.get('retention_days', 30)
        types = options.get('backup_types', ['full', 'incremental'])
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for backup_type in types:
            backup_dir = os.path.join(self.backup_path, backup_type)
            if not os.path.exists(backup_dir):
                continue
                
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    self.logger.info(f"Removed old backup: {filepath}")

    def _cleanup_temp_files(self, task: MaintenanceTask) -> None:
        """Cleans up temporary database files."""
        options = task.options or {}
        file_pattern = options.get('file_pattern', '*.tmp')
        
        temp_dir = self._get_temp_directory()
        
        import glob
        for filepath in glob.glob(os.path.join(temp_dir, file_pattern)):
            try:
                os.remove(filepath)
                self.logger.info(f"Removed temp file: {filepath}")
            except Exception as e:
                self.logger.error(f"Failed to remove temp file: {str(e)}")

    def _cleanup_dead_rows(self, task: MaintenanceTask) -> None:
        """Cleans up dead rows from table."""
        options = task.options or {}
        batch_size = options.get('batch_size', 1000)
        
        cleanup_sql = f"""
            DELETE FROM {task.target}
            WHERE ctid IN (
                SELECT ctid
                FROM {task.target}
                WHERE xmin < pg_snapshot_xmin(pg_current_snapshot())
                LIMIT {batch_size}
            )
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(cleanup_sql)

    def _optimize_table(self, task: MaintenanceTask) -> None:
        """Optimizes table storage and statistics."""
        options = task.options or {}
        rebuild = options.get('rebuild', False)
        
        if rebuild:
            # Rebuild table
            rebuild_sql = f"""
                CREATE TABLE {task.target}_new (LIKE {task.target} INCLUDING ALL);
                INSERT INTO {task.target}_new SELECT * FROM {task.target};
                DROP TABLE {task.target};
                ALTER TABLE {task.target}_new RENAME TO {task.target};
            """
            with self.connection.cursor() as cursor:
                cursor.execute(rebuild_sql)
        
        # Update statistics
        analyze_sql = f"ANALYZE VERBOSE {task.target}"
        with self.connection.cursor() as cursor:
            cursor.execute(analyze_sql)

    def _optimize_indexes(self, task: MaintenanceTask) -> None:
        """Optimizes table indexes."""
        options = task.options or {}
        concurrent = options.get('concurrent', True)
        
        # Get table indexes
        index_sql = f"""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = %s
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(index_sql, [task.target])
            indexes = cursor.fetchall()
            
            # Reindex each index
            for index in indexes:
                reindex_sql = f"REINDEX {'CONCURRENTLY' if concurrent else ''} INDEX {index[0]}"
                cursor.execute(reindex_sql)

    def _optimize_cache(self, task: MaintenanceTask) -> None:
        """Optimizes database cache settings."""
        options = task.options or {}
        cache_size = options.get('cache_size', None)
        shared_buffers = options.get('shared_buffers', None)
        
        if cache_size:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SET effective_cache_size = '{cache_size}MB'")
        
        if shared_buffers:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SET shared_buffers = '{shared_buffers}MB'")

    def get_maintenance_status(self) -> Dict[str, Any]:
        """
        Gets maintenance status information.
        
        Returns:
            Dictionary with maintenance status
            
        Example:
            status = manager.get_maintenance_status()
            print(f"Pending tasks: {status['pending_tasks']}")
        """
        return {
            "pending_tasks": self.task_queue.qsize(),
            "scheduler_active": self._scheduler_thread is not None and self._scheduler_thread.is_alive(),
            "last_maintenance": self.maintenance_history[-1] if self.maintenance_history else None,
            "total_tasks_completed": len(self.maintenance_history),
            "failed_tasks": sum(1 for task in self.maintenance_history if task["status"] == "ERROR"),
            "backup_status": self._get_backup_status()
        }

def _get_backup_status(self) -> Dict[str, Any]:
        """Gets backup-related status information."""
        if not self.backup_path:
            return {"enabled": False}
            
        full_backups = os.path.join(self.backup_path, 'full')
        incremental_backups = os.path.join(self.backup_path, 'incremental')
        
        return {
            "enabled": True,
            "backup_path": self.backup_path,
            "full_backups": len(os.listdir(full_backups)) if os.path.exists(full_backups) else 0,
            "incremental_backups": len(os.listdir(incremental_backups)) if os.path.exists(incremental_backups) else 0,
            "last_backup": self._get_last_backup_info(),
            "storage_usage": self._get_backup_storage_usage(),
            "backup_health": self._check_backup_health()
        }

    def _get_last_backup_info(self) -> Dict[str, Any]:
        """Gets information about the last backup."""
        if not self.backup_path:
            return None
            
        last_backup = None
        last_backup_time = None
        
        # Check both full and incremental directories
        for backup_type in ['full', 'incremental']:
            backup_dir = os.path.join(self.backup_path, backup_type)
            if not os.path.exists(backup_dir):
                continue
                
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                
                if not last_backup_time or file_time > last_backup_time:
                    last_backup = {
                        "file": filename,
                        "type": backup_type,
                        "time": file_time,
                        "size": os.path.getsize(filepath)
                    }
                    last_backup_time = file_time
        
        return last_backup

    def _get_backup_storage_usage(self) -> Dict[str, Any]:
        """Calculates backup storage usage."""
        if not self.backup_path:
            return None
            
        usage = {
            "total_size": 0,
            "full_backups_size": 0,
            "incremental_backups_size": 0,
            "available_space": 0
        }
        
        # Calculate sizes for each backup type
        for backup_type in ['full', 'incremental']:
            backup_dir = os.path.join(self.backup_path, backup_type)
            if not os.path.exists(backup_dir):
                continue
                
            type_size = sum(
                os.path.getsize(os.path.join(backup_dir, f))
                for f in os.listdir(backup_dir)
            )
            
            if backup_type == 'full':
                usage["full_backups_size"] = type_size
            else:
                usage["incremental_backups_size"] = type_size
        
        usage["total_size"] = usage["full_backups_size"] + usage["incremental_backups_size"]
        
        # Get available space
        backup_stats = os.statvfs(self.backup_path)
        usage["available_space"] = backup_stats.f_frsize * backup_stats.f_bavail
        
        return usage

    def _check_backup_health(self) -> Dict[str, Any]:
        """Checks health of backup system."""
        if not self.backup_path:
            return None
            
        health = {
            "status": "HEALTHY",
            "issues": []
        }
        
        # Check backup frequency
        last_backup = self._get_last_backup_info()
        if last_backup:
            backup_age = datetime.now() - last_backup["time"]
            if backup_age > timedelta(days=7):
                health["status"] = "WARNING"
                health["issues"].append("No recent backups")
        
        # Check storage space
        storage = self._get_backup_storage_usage()
        if storage:
            available_gb = storage["available_space"] / (1024 * 1024 * 1024)
            if available_gb < 10:  # Less than 10GB available
                health["status"] = "WARNING"
                health["issues"].append("Low storage space")
        
        # Check backup integrity
        for backup_type in ['full', 'incremental']:
            backup_dir = os.path.join(self.backup_path, backup_type)
            if not os.path.exists(backup_dir):
                continue
                
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                if not self._verify_backup_integrity(filepath):
                    health["status"] = "ERROR"
                    health["issues"].append(f"Corrupt backup: {filename}")
        
        return health

    def _verify_backup_integrity(self, backup_path: str) -> bool:
        """Verifies integrity of backup file."""
        try:
            # Basic file integrity check
            if os.path.getsize(backup_path) == 0:
                return False
            
            # Read first and last block to ensure file is readable
            with open(backup_path, 'rb') as f:
                # Read first block
                f.seek(0)
                first_block = f.read(8192)
                if not first_block:
                    return False
                
                # Read last block
                f.seek(-8192, 2)
                last_block = f.read()
                if not last_block:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup integrity check failed: {str(e)}")
            return False

    def generate_maintenance_report(self, 
                                 format: str = 'text',
                                 file_path: Optional[str] = None) -> Optional[str]:
        """
        Generates maintenance activity report.
        
        Args:
            format: Report format ('text', 'json', 'html')
            file_path: Optional file path to save report
            
        Returns:
            Report content if no file_path provided
            
        Example:
            # Generate text report
            report = manager.generate_maintenance_report('text')
            print(report)
            
            # Save HTML report
            manager.generate_maintenance_report('html', 'maintenance_report.html')
        """
        if format == 'text':
            report = self._generate_text_report()
        elif format == 'json':
            report = self._generate_json_report()
        elif format == 'html':
            report = self._generate_html_report()
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(report)
            return None
        
        return report

    def _generate_text_report(self) -> str:
        """Generates text format maintenance report."""
        lines = []
        lines.append("Database Maintenance Report")
        lines.append("=" * 30)
        
        # Summary
        status = self.get_maintenance_status()
        lines.append(f"Pending Tasks: {status['pending_tasks']}")
        lines.append(f"Total Tasks Completed: {status['total_tasks_completed']}")
        lines.append(f"Failed Tasks: {status['failed_tasks']}")
        lines.append("")
        
        # Backup Status
        backup_status = status['backup_status']
        if backup_status['enabled']:
            lines.append("Backup Status")
            lines.append("-" * 20)
            lines.append(f"Full Backups: {backup_status['full_backups']}")
            lines.append(f"Incremental Backups: {backup_status['incremental_backups']}")
            if backup_status.get('last_backup'):
                lines.append(f"Last Backup: {backup_status['last_backup']['time']}")
            lines.append("")
        
        # Recent Tasks
        lines.append("Recent Maintenance Tasks")
        lines.append("-" * 20)
        for task in self.maintenance_history[-10:]:  # Last 10 tasks
            lines.append(f"Type: {task['task_type']}")
            lines.append(f"Target: {task['target']}")
            lines.append(f"Status: {task['status']}")
            if task['error']:
                lines.append(f"Error: {task['error']}")
            lines.append("")
        
        return "\n".join(lines)

### Final Integration Patterns and Best Practices Summary

#### 1. Integration Patterns

```python
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
import logging
from contextlib import contextmanager
from enum import Enum
import threading
import queue
import time

class IntegrationType(Enum):
    """Types of database integrations."""
    DIRECT = "DIRECT"                  # Direct database connection
    POOLED = "POOLED"                  # Connection pool
    READONLY_REPLICA = "READONLY"      # Read-only replica
    LOAD_BALANCED = "LOAD_BALANCED"    # Load-balanced cluster
    FAILOVER = "FAILOVER"             # Failover configuration

@dataclass
class IntegrationConfig:
    """Configuration for database integration."""
    integration_type: IntegrationType
    primary_connection: Any
    secondary_connections: Optional[List[Any]] = None
    failover_strategy: str = "automatic"  # automatic, manual, supervised
    load_balance_strategy: str = "round_robin"  # round_robin, least_connections, weighted
    max_retries: int = 3
    retry_delay: int = 5
    health_check_interval: int = 60

class DatabaseIntegrationManager:
    """Manages database integration patterns and strategies."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize integration manager.
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection_status = {}
        self.active_connection = None
        self._health_check_thread = None
        self._should_run = False
        self._connection_locks = {}
        self._connection_stats = {}
        self._initialize_integration()

    def _initialize_integration(self) -> None:
        """Initializes integration based on configuration."""
        if self.config.integration_type == IntegrationType.POOLED:
            self._initialize_connection_pool()
        elif self.config.integration_type == IntegrationType.LOAD_BALANCED:
            self._initialize_load_balancer()
        elif self.config.integration_type == IntegrationType.FAILOVER:
            self._initialize_failover()
        
        # Start health checking
        self.start_health_checker()

    def _initialize_connection_pool(self) -> None:
        """Initializes connection pool."""
        self.connection_pool = queue.Queue()
        self.pool_semaphore = threading.Semaphore(10)  # Max pool size
        
        # Create initial pool connections
        for _ in range(5):  # Initial pool size
            connection = self._create_new_connection()
            if connection:
                self.connection_pool.put(connection)

    def _initialize_load_balancer(self) -> None:
        """Initializes load balancer."""
        self.available_connections = []
        self.connection_weights = {}
        
        # Add primary connection
        self.available_connections.append(self.config.primary_connection)
        self.connection_weights[id(self.config.primary_connection)] = 100  # Default weight
        
        # Add secondary connections
        if self.config.secondary_connections:
            for conn in self.config.secondary_connections:
                self.available_connections.append(conn)
                self.connection_weights[id(conn)] = 50  # Lower weight for secondaries

    def _initialize_failover(self) -> None:
        """Initializes failover configuration."""
        self.failover_status = {
            'primary_healthy': True,
            'failover_active': False,
            'last_failover': None,
            'failover_count': 0
        }
        
        # Initialize connection monitoring
        self.connection_status[id(self.config.primary_connection)] = {
            'healthy': True,
            'last_check': datetime.now(),
            'error_count': 0
        }
        
        if self.config.secondary_connections:
            for conn in self.config.secondary_connections:
                self.connection_status[id(conn)] = {
                    'healthy': True,
                    'last_check': datetime.now(),
                    'error_count': 0
                }

    def start_health_checker(self) -> None:
        """Starts health check thread."""
        if self._health_check_thread is not None:
            return
            
        self._should_run = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()

    def stop_health_checker(self) -> None:
        """Stops health check thread."""
        self._should_run = False
        if self._health_check_thread:
            self._health_check_thread.join()
            self._health_check_thread = None

    def _health_check_loop(self) -> None:
        """Main health check loop."""
        while self._should_run:
            try:
                self._check_all_connections()
                time.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check error: {str(e)}")

    def _check_all_connections(self) -> None:
        """Checks health of all connections."""
        # Check primary connection
        primary_healthy = self._check_connection(self.config.primary_connection)
        self.connection_status[id(self.config.primary_connection)]['healthy'] = primary_healthy
        
        # Check secondary connections
        if self.config.secondary_connections:
            for conn in self.config.secondary_connections:
                conn_healthy = self._check_connection(conn)
                self.connection_status[id(conn)]['healthy'] = conn_healthy
        
        # Handle failover if needed
        if self.config.integration_type == IntegrationType.FAILOVER:
            self._handle_failover_status()

    def _check_connection(self, connection: Any) -> bool:
        """Checks if connection is healthy."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            self.logger.error(f"Connection check failed: {str(e)}")
            return False

    def _handle_failover_status(self) -> None:
        """Handles failover status changes."""
        primary_status = self.connection_status[id(self.config.primary_connection)]
        
        if not primary_status['healthy'] and not self.failover_status['failover_active']:
            if self.config.failover_strategy == "automatic":
                self._initiate_failover()
            elif self.config.failover_strategy == "supervised":
                self._request_failover_supervision()
        
        elif primary_status['healthy'] and self.failover_status['failover_active']:
            if self.config.failover_strategy == "automatic":
                self._initiate_failback()

    def _initiate_failover(self) -> None:
        """Initiates failover to secondary connection."""
        if not self.config.secondary_connections:
            self.logger.error("No secondary connections available for failover")
            return
        
        # Find healthy secondary
        for conn in self.config.secondary_connections:
            if self.connection_status[id(conn)]['healthy']:
                self.active_connection = conn
                self.failover_status['failover_active'] = True
                self.failover_status['last_failover'] = datetime.now()
                self.failover_status['failover_count'] += 1
                
                self.logger.warning("Failover initiated to secondary connection")
                return
        
        self.logger.error("No healthy secondary connections available")

    def _initiate_failback(self) -> None:
        """Initiates failback to primary connection."""
        self.active_connection = self.config.primary_connection
        self.failover_status['failover_active'] = False
        self.logger.info("Failed back to primary connection")

    def get_connection(self) -> Any:
        """
        Gets appropriate database connection based on integration type.
        
        Returns:
            Database connection
            
        Example:
            with integration_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users")
        """
        if self.config.integration_type == IntegrationType.POOLED:
            return self._get_pooled_connection()
        elif self.config.integration_type == IntegrationType.LOAD_BALANCED:
            return self._get_load_balanced_connection()
        elif self.config.integration_type == IntegrationType.FAILOVER:
            return self._get_failover_connection()
        else:
            return self.config.primary_connection

    def _get_pooled_connection(self) -> Any:
        """Gets connection from pool."""
        try:
            # Try to get existing connection
            connection = self.connection_pool.get_nowait()
            
            # Verify connection is still good
            if self._check_connection(connection):
                return connection
            
            # Connection bad, create new one
            return self._create_new_connection()
            
        except queue.Empty:
            # Pool empty, create new connection if allowed
            with self.pool_semaphore:
                return self._create_new_connection()

    def _get_load_balanced_connection(self) -> Any:
        """Gets connection based on load balancing strategy."""
        if self.config.load_balance_strategy == "round_robin":
            return self._round_robin_connection()
        elif self.config.load_balance_strategy == "least_connections":
            return self._least_connections()
        elif self.config.load_balance_strategy == "weighted":
            return self._weighted_connection()
        else:
            return self.available_connections[0]

    def _get_failover_connection(self) -> Any:
        """Gets appropriate connection based on failover status."""
        if self.failover_status['failover_active']:
            # Use secondary during failover
            for conn in self.config.secondary_connections:
                if self.connection_status[id(conn)]['healthy']:
                    return conn
            
            # No healthy secondary, try primary
            if self.connection_status[id(self.config.primary_connection)]['healthy']:
                self.failover_status['failover_active'] = False
                return self.config.primary_connection
                
            raise DatabaseError("No healthy connections available")
        else:
            # Use primary normally
            return self.config.primary_connection

    def _round_robin_connection(self) -> Any:
        """Implements round-robin connection selection."""
        with threading.Lock():
            # Move first connection to end
            conn = self.available_connections.pop(0)
            self.available_connections.append(conn)
            return conn

    def _least_connections(self) -> Any:
        """Implements least connections selection."""
        min_connections = float('inf')
        selected_conn = None
        
        for conn in self.available_connections:
            curr_connections = self._connection_stats.get(id(conn), {}).get('active_connections', 0)
            if curr_connections < min_connections:
                min_connections = curr_connections
                selected_conn = conn
        
        return selected_conn or self.available_connections[0]

    def _weighted_connection(self) -> Any:
        """Implements weighted connection selection."""
        total_weight = sum(self.connection_weights.values())
        if total_weight == 0:
            return self.available_connections[0]
            
        selection = random.randint(1, total_weight)
        current_weight = 0
        
        for conn in self.available_connections:
            current_weight += self.connection_weights[id(conn)]
            if selection <= current_weight:
                return conn
        
        return self.available_connections[0]

    def _create_new_connection(self) -> Any:
        """Creates new database connection."""
        for _ in range(self.config.max_retries):
            try:
                # Use primary connection settings
                if isinstance(self.config.primary_connection, str):
                    # Connection string
                    return self.create_connection(self.config.primary_connection)
                else:
                    # Connection object - clone it
                    return self.clone_connection(self.config.primary_connection)
            except Exception as e:
                self.logger.error(f"Connection creation failed: {str(e)}")
                time.sleep(self.config.retry_delay)
        
        raise DatabaseError("Failed to create new connection")

    @contextmanager
    def connection(self, readonly: bool = False) -> Any:
        """
        Context manager for database connections.
        
        Args:
            readonly: Whether connection is for read-only operations
            
        Example:
            with integration_manager.connection(readonly=True) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users")
        """
        connection = None
        try:
            connection = self.get_connection()
            if readonly and self.config.integration_type == IntegrationType.READONLY_REPLICA:
                connection = self._get_readonly_connection()
            
            # Track connection usage
            conn_id = id(connection)
            self._connection_stats.setdefault(conn_id, {})['active_connections'] = \
                self._connection_stats[conn_id].get('active_connections', 0) + 1
            
            yield connection
            
        finally:
            if connection:
                # Update connection stats
                conn_id = id(connection)
                self._connection_stats[conn_id]['active_connections'] -= 1
                
                # Return to pool if pooled
                if self.config.integration_type == IntegrationType.POOLED:
                    self.connection_pool.put(connection)

    def _get_readonly_connection(self) -> Any:
        """Gets connection from read-only replica."""
        if not self.config.secondary_connections:
            return self.config.primary_connection
            
        # Find healthy secondary
        for conn in self.config.secondary_connections:
            if self.connection_status[id(conn)]['healthy']:
                return conn
        
        # No healthy secondary, use primary
        return self.config.primary_connection

    def get_integration_status(self) -> Dict[str, Any]:
        """
        Gets integration status information.
        
        Returns:
            Dictionary with integration status
            
        Example:
            status = integration_manager.get_integration_status()
            print(f"Active connections: {status['active_connections']}")
        """
        return {
            "integration_type": self.config.integration_type.value,
            "active_connections": sum(
                stats['active_connections']
                for stats in self._connection_stats.values()
            ),
            "connection_health": {
                conn_id: status
                for conn_id, status in self.connection_status.items()
            },
            "failover_status": self.failover_status if hasattr(self, 'failover_status') else None,
            "pool_status": {
                "available_connections": self.connection_pool.qsize()
            } if self.config.integration_type == IntegrationType.POOLED else None
        }
```

[🔝 Back to Table of Contents](#table-of-contents)

#### 2. Best Practices Summary

1. Connection Management
   - Use connection pooling for better resource utilization
   - Implement proper connection cleanup
   - Monitor connection health regularly
   - Use appropriate timeouts and retry strategies

2. Transaction Management
   - Use explicit transactions for multi-statement operations
   - Implement proper rollback mechanisms
   - Consider distributed transaction patterns when needed
   - Monitor transaction durations

3. Security Considerations
   - Implement proper credential management
   - Use connection encryption when available
   - Implement proper access controls
   - Regular security audits

4. Performance Optimization
   - Use connection pooling
   - Implement proper caching strategies
   - Monitor and optimize query performance
        

[🔝 Back to Table of Contents](#table-of-contents)

## ✨ Best Practices <a name="best-practices"></a>

### 🔄 Connection Management <a name="connection-management"></a>
1. Connection Pool Best Practices
   - Set appropriate pool sizes based on workload
   - Implement connection validation before reuse
   - Monitor and log pool statistics
   - Implement proper cleanup routines

2. Transaction Handling
   - Use explicit transaction boundaries
   - Implement proper timeout mechanisms
   - Handle distributed transactions carefully
   - Monitor transaction durations

3. Resource Management
   - Implement proper connection cleanup
   - Use connection timeouts
   - Monitor connection leaks
   - Implement connection validation

[🔝 Back to Table of Contents](#table-of-contents)

### 🔒 Security Practices <a name="security-practices"></a>
1. Authentication
   - Use strong authentication methods
   - Implement proper credential management
   - Regular credential rotation
   - Monitor authentication failures

2. Encryption
   - Use SSL/TLS for connections
   - Implement proper certificate management
   - Regular certificate updates
   - Monitor encryption status

3. Access Control
   - Implement principle of least privilege
   - Regular access audits
   - Monitor unauthorized access attempts
   - Implement proper role management

[🔝 Back to Table of Contents](#table-of-contents)

### ⚡ Performance Optimization <a name="performance-optimization"></a>
1. Query Optimization
   - Regular query analysis
   - Implement proper indexing
   - Monitor query performance
   - Optimize large queries

2. Resource Utilization
   - Monitor memory usage
   - Optimize connection usage
   - Implement proper caching
   - Regular performance audits

3. Scaling Strategies
   - Implement proper load balancing
   - Consider read replicas
   - Monitor scaling metrics
   - Implement proper sharding strategies

[🔝 Back to Table of Contents](#table-of-contents)

## ❌ Error Handling <a name="error-handling"></a>

### 🌳 Exception Hierarchy <a name="exception-hierarchy"></a>
1. Database Exceptions
   - Connection errors
   - Query errors
   - Transaction errors
   - Resource errors

2. Custom Exceptions
   - Business logic exceptions
   - Validation exceptions
   - Security exceptions
   - Configuration exceptions

[🔝 Back to Table of Contents](#table-of-contents)

### 🎯 Error Handling Patterns <a name="error-handling-patterns"></a>
1. Retry Patterns
   - Implement exponential backoff
   - Set maximum retry attempts
   - Handle transient errors
   - Log retry attempts

2. Fallback Strategies
   - Implement circuit breakers
   - Define fallback behaviors
   - Handle degraded operations
   - Monitor fallback usage

[🔝 Back to Table of Contents](#table-of-contents)

### 📝 Logging and Monitoring <a name="logging-and-monitoring"></a>
1. Log Management
   - Implement structured logging
   - Define log levels
   - Implement log rotation
   - Monitor log patterns

2. Performance Monitoring
   - Monitor query performance
   - Track resource usage
   - Implement alerts
   - Regular performance reviews

[🔝 Back to Table of Contents](#table-of-contents)

## 🔧 Troubleshooting Guide <a name="troubleshooting-guide"></a>

### ❗ Common Issues and Solutions <a name="common-issues-and-solutions"></a>
1. Connection Issues
   - Connection timeouts
   - Authentication failures
   - Resource exhaustion
   - Network problems

2. Performance Issues
   - Slow queries
   - Resource contention
   - Memory problems
   - Deadlocks

[🔝 Back to Table of Contents](#table-of-contents)

### 🔍 Diagnostic Tools <a name="diagnostic-tools"></a>
1. Monitoring Tools
   - Query analyzers
   - Performance monitors
   - Resource trackers
   - Log analyzers

2. Debugging Tools
   - Query profilers
   - Connection tracers
   - Memory analyzers
   - Stack tracers

[🔝 Back to Table of Contents](#table-of-contents)

### 🛠️ Maintenance Procedures <a name="maintenance-procedures"></a>
1. Regular Maintenance
   - Database cleanup
   - Index maintenance
   - Statistics updates
   - Backup verification

2. Emergency Procedures
   - Failover procedures
   - Recovery procedures
   - Emergency contacts
   - Incident response

[🔝 Back to Table of Contents](#table-of-contents)


