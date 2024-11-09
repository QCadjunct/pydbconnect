# Database Connection Constants Documentation

## Table of Contents

1. [Overview](#overview)
2. [Helper Functions](#helper-functions)
3. [Database Engine Configurations](#database-engine-configurations)
4. [Common Usage Patterns](#common-usage-patterns)
5. [Engine-Specific Examples](#engine-specific-examples)
6. [Advanced Use Cases](#advanced-use-cases)

## Overview

The database_connection_constants module provides configuration templates and connection management for multiple database engines. Each engine's configuration follows a consistent structure while accommodating engine-specific requirements.

### Key Features

- Dynamic module imports
- Secure credential handling
- DSN and direct connection support
- Customizable connection strings

## Helper Functions

### Dynamic Module Import

```python
def get_db_target_engine_module(module_name: str) -> Any:
    """Dynamically imports database modules"""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}. Make sure it's installed.") from e

# Usage example
try:
    psycopg2 = get_db_target_engine_module('psycopg2')
except ImportError:
    print("Please install psycopg2 first")
```

### Parameter Loading

```python
def load_default_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """Loads default parameters excluding sensitive data"""
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
    return {
        key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
        for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]
    }

# Example usage
params = load_default_parameter_keys_dict("MSSQL", MSSQL)
print("Secure parameters:", params)
```

## Database Engine Configurations

### Structure Overview

Each database engine configuration follows this structure:

```python
ENGINE_CONFIG = {
    "ENGINE_NAME": {
        "DEFAULT_PARAMETERS": {
            # Connection parameters
            "DRIVER": "...",
            "SERVER": "...",
            # Connection string formatting
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [...],
                "IS_DSN_NAME_SUPPORTED": bool,
                "BASE_CONNECTION_STRING": "...",
            }
        },
        "CRUDBASIC": {
            "IMPORT": "module_name",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": bool
        }
    }
}
```

## Common Usage Patterns

### 1. Basic Connection Setup

```python
# MSSQL Connection Example
def create_mssql_connection():
    config = MSSQL["MSSQL"]
    conn_str = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MSSQL)
    
    connection_func = config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_str)
    return connection_func()

# PostgreSQL with psycopg2
def create_postgres_connection():
    config = PSYCOPG2["PSYCOPG2"]
    conn_str = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG2)
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_str)()
```

### 2. DSN Connection Handling

```python
def connect_with_dsn(engine_config: dict, dsn_name: str):
    if not engine_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["IS_DSN_NAME_SUPPORTED"]:
        raise ValueError("DSN not supported for this engine")
    
    conn_str = engine_config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](
        {"DSN_NAME": dsn_name}
    )
    return engine_config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_str)()
```

## Engine-Specific Examples

### 1. MSSQL with Windows Authentication

```python
def mssql_windows_auth():
    config = MSSQL["MSSQL"]
    custom_params = {
        "DRIVER": "{ODBC Driver 17 for SQL Server}",
        "SERVER": "localhost",
        "DATABASE_NAME": "master",
        "Trusted_Connection": "yes"
    }
    
    conn_str = "DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection={3}".format(
        custom_params["DRIVER"],
        custom_params["SERVER"],
        custom_params["DATABASE_NAME"],
        custom_params["Trusted_Connection"]
    )
    
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](conn_str)()
```

### 2. PostgreSQL with SSL

```python
def postgres_ssl_connection():
    config = POSTGRESQL["POSTGRESQL"]
    custom_params = {
        **config["DEFAULT_PARAMETERS"],
        "sslmode": "verify-full",
        "sslcert": "/path/to/client-cert.pem",
        "sslkey": "/path/to/client-key.pem",
        "sslrootcert": "/path/to/server-ca.pem"
    }
    
    conn_str = "host={SERVER};port={PORT_NUMBER};dbname={DATABASE_NAME};" \
               "user={USERNAME};password={PASSWORD};" \
               "sslmode={sslmode};sslcert={sslcert};sslkey={sslkey};sslrootcert={sslrootcert}"
               
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](
        conn_str.format(**custom_params)
    )()
```

### 3. SQLite3 with Custom Settings

```python
def sqlite_optimized_connection():
    config = SQLITE3["SQLITE3"]
    custom_params = {
        "DRIVER": config["DEFAULT_PARAMETERS"]["DRIVER"],
        "DATABASE_NAME": ":memory:",  # In-memory database
        "TIMEOUT": 30,
        "CACHE_SIZE": 2000,
        "PAGE_SIZE": 4096
    }
    
    conn_str = "DRIVER={DRIVER};DATABASE={DATABASE_NAME};" \
               "TIMEOUT={TIMEOUT};CACHE_SIZE={CACHE_SIZE};PAGE_SIZE={PAGE_SIZE}"
               
    return config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](
        conn_str.format(**custom_params)
    )()
```

## Advanced Use Cases

### 1. Connection Pool Manager

```python
class DatabasePoolManager:
    def __init__(self, engine_type: str, max_connections: int = 5):
        self.engine_config = globals()[engine_type][engine_type]
        self.pool = []
        self.max_connections = max_connections
        
    def get_connection(self):
        if not self.pool:
            conn_str = self.engine_config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](
                globals()[self.engine_type]
            )
            new_conn = self.engine_config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](
                conn_str
            )()
            return new_conn
        return self.pool.pop()
    
    def return_connection(self, conn):
        if len(self.pool) < self.max_connections:
            self.pool.append(conn)
        else:
            conn.close()
```

### 2. Multi-Database Manager

```python
class MultiDatabaseManager:
    def __init__(self):
        self.connections = {}
        
    def add_connection(self, name: str, engine_type: str, **params):
        config = globals()[engine_type][engine_type]
        custom_params = {**config["DEFAULT_PARAMETERS"], **params}
        
        conn_str = config["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](
            {engine_type: {"DEFAULT_PARAMETERS": custom_params}}
        )
        
        self.connections[name] = config["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](
            conn_str
        )()
        
    def execute_query(self, db_name: str, query: str):
        if db_name not in self.connections:
            raise ValueError(f"No connection found for {db_name}")
        with self.connections[db_name].cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
```
