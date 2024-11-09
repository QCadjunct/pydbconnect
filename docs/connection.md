# PyDBConnect - Database Connection Library

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Connection Management](#connection-management)
5. [Query Execution](#query-execution)
6. [Advanced Features](#advanced-features)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Overview

PyDBConnect provides a fluent interface for managing database connections across multiple database engines. The library emphasizes type safety, credential security, and ease of use through method chaining.

```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine, TargetDatabaseConnectionStringOption

# Simple connection example
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).change_default_username_and_password(True) \
 .finalization_of_connection_parameters(
    host="localhost", 
    port=1433, 
    database="Northwind"
) \
 .connect_to_database()
```

## Installation

```bash
pip install pydbconnect
```

## Basic Usage

### 1. Creating a Connection

The DatabaseConnection class supports multiple database engines through a flexible configuration system.

```python
# Basic MSSQL connection
db_mssql = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)

# PostgreSQL with custom credentials
db_psql = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd,
    key_management='.env'
)

# SQLite without authentication
db_sqlite = DatabaseConnection(
    TargetDatabaseEngine.SQLITE3,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)
```

### 2. Connection Parameters

Parameters can be set using the fluent interface:

```python
db = DatabaseConnection(TargetDatabaseEngine.MSSQL) \
    .finalization_of_connection_parameters(
        host="localhost",
        port=1433,
        database="Northwind",
        trusted_connection="yes"
    )
```

## Connection Management

### 1. Credential Management

The library provides secure credential management through environment variables:

```python
# Environment file (.env) structure:
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password
POSTGRES_USERNAME=pg_user
POSTGRES_PASSWORD=pg_pass

# In code:
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).change_default_username_and_password(show_password=False)
```

### 2. Connection String Options

Different connection methods are supported through the TargetDatabaseConnectionStringOption enum:

```python
# Standard connection
standard_conn = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)

# DSN-based connection
dsn_conn = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.Default_DSN_AndDefaultUserPwd
)
```

## Query Execution

### 1. Basic Queries with PrettyTable

```python
# Execute and print results
db.execute_sql_to_prettytable(
    "SELECT TOP 5 * FROM Customers", 
    is_print=True
)

# Return results as PrettyTable object
results = db.execute_sql_to_prettytable(
    "SELECT * FROM Orders WHERE OrderDate > '2020-01-01'"
)
```

### 2. Pandas Integration

```python
# Query to DataFrame
df = db.execute_sql_to_panda_dataframe(
    "SELECT * FROM Products",
    index_column="ProductID"
)

# Chain operations
db.execute_sql_to_panda_dataframe(
    "SELECT * FROM Orders",
    return_dataframe=False
) \
  .df_to_parquet_buffer()
```

## Advanced Features

### 1. Custom Parameter Handling

The `@preload_default_parameters` decorator manages parameter loading:

```python
@preload_default_parameters(_get_default_parameters)
def finalization_of_connection_parameters(self, **custom_params):
    """
    Finalizes connection parameters with custom overrides.
    
    Example:
    -------
    db.finalization_of_connection_parameters(
        host="custom.host",
        port=1234,
        database="custom_db"
    )
    """
    # Implementation details...
```

### 2. Connection String Building

```python
db = DatabaseConnection(TargetDatabaseEngine.PSYCOPG2)
db._build_finalization_connection_parameters_string()
# Results in: "host=localhost; port=5432; database=mydb; user=user; password=pass;"
```

## Best Practices

### 1. Environment Management

Always use environment variables for sensitive data:

```python
# .env
DEFAULT_KEY_MANAGEMENT_ENV_FILE=path/to/env/file
MSSQL_USERNAME=admin
MSSQL_PASSWORD=secure_password

# code
import os
from dotenv import load_dotenv

load_dotenv()
env_file = os.getenv('DEFAULT_KEY_MANAGEMENT_ENV_FILE', '.env')

db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    key_management=env_file
)
```

### 2. Error Handling

```python
try:
    db = DatabaseConnection(TargetDatabaseEngine.MSSQL) \
        .finalization_of_connection_parameters(
            host="localhost",
            database="NonExistentDB"
        ) \
        .connect_to_database()
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

## Examples

### 1. Complete Data Analysis Flow

```python
# Connect to database and perform analysis
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).change_default_username_and_password(True) \
 .finalization_of_connection_parameters(
    host="localhost",
    port=1433,
    database="Sales"
) \
 .connect_to_database()

# Get sales data
sales_df = db.execute_sql_to_panda_dataframe("""
    SELECT 
        YEAR(OrderDate) as Year,
        MONTH(OrderDate) as Month,
        SUM(Amount) as TotalSales
    FROM Orders
    GROUP BY YEAR(OrderDate), MONTH(OrderDate)
    ORDER BY Year, Month
""")

# Export to parquet
parquet_buffer = db.df_to_parquet_buffer(sales_df)
```

### 2. Multi-Database Operations

```python
# Source database (MSSQL)
source_db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
).finalization_of_connection_parameters(
    host="source.host",
    database="SourceDB"
).connect_to_database()

# Target database (PostgreSQL)
target_db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).change_default_username_and_password(True) \
 .finalization_of_connection_parameters(
    host="target.host",
    port=5432,
    database="TargetDB"
) \
 .connect_to_database()

# Transfer data
data = source_db.execute_sql_to_panda_dataframe(
    "SELECT * FROM SourceTable"
)
# Process data as needed...
```

### 3. Real-time Monitoring

```python
import time

def monitor_orders():
    db = DatabaseConnection(
        TargetDatabaseEngine.MSSQL,
        TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
    ).finalization_of_connection_parameters(
        host="localhost",
        database="Orders"
    ).connect_to_database()
    
    while True:
        results = db.execute_sql_to_prettytable("""
            SELECT 
                COUNT(*) as PendingOrders,
                SUM(Amount) as TotalValue
            FROM Orders
            WHERE Status = 'Pending'
        """, is_print=True)
        
        time.sleep(60)  # Check every minute
```

This documentation provides a comprehensive guide to using the PyDBConnect library, with practical examples and best practices. The code samples demonstrate real-world usage scenarios while maintaining security and proper error handling.

Would you like me to expand on any particular section or add more specific examples?