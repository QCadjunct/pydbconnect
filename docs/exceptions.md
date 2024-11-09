# Database Connection Exceptions Documentation

## Table of Contents
1. [Overview](#overview)
2. [Exception Types](#exception-types)
3. [Usage Patterns](#usage-patterns)
4. [Best Practices](#best-practices)
5. [Practical Examples](#practical-examples)

## Overview

The exceptions module provides custom exception handling for database connections, enhancing error reporting and handling in PyDBConnect.

```python
class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass
```

## Exception Types

### DatabaseConnectionError
This is the base exception class for all database connection-related errors. It inherits from Python's built-in `Exception` class.

```python
try:
    db = DatabaseConnection(TargetDatabaseEngine.MSSQL)
    db.connect()
except DatabaseConnectionError as e:
    print(f"Failed to connect: {e}")
```

## Usage Patterns

### 1. Basic Error Handling

```python
from pydbconnect.exceptions import DatabaseConnectionError

def connect_to_database():
    try:
        db = DatabaseConnection(
            TargetDatabaseEngine.MYSQL,
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        ).finalization_of_connection_parameters(
            host="localhost",
            port=3306,
            database="users"
        ).connect_to_database()
        return db
    except DatabaseConnectionError as e:
        logging.error(f"Database connection failed: {e}")
        raise
```

### 2. Error Handling with Recovery

```python
class DatabaseManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
    
    def connect_with_retry(self):
        attempts = 0
        while attempts < self.max_retries:
            try:
                return DatabaseConnection(
                    TargetDatabaseEngine.POSTGRESQL
                ).connect_to_database()
            except DatabaseConnectionError as e:
                attempts += 1
                if attempts == self.max_retries:
                    raise
                time.sleep(1)  # Wait before retrying
```

### 3. Contextual Error Handling

```python
def execute_query(query: str) -> Optional[pd.DataFrame]:
    try:
        db = DatabaseConnection(TargetDatabaseEngine.MSSQL)
        return db.execute_sql_to_panda_dataframe(query)
    except DatabaseConnectionError as e:
        logging.error(f"Connection error during query execution: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
```

## Best Practices

### 1. Custom Error Messages

```python
class DatabaseOperations:
    def __init__(self, connection_params: dict):
        try:
            self.db = DatabaseConnection(
                TargetDatabaseEngine.MSSQL
            ).finalization_of_connection_parameters(**connection_params)
        except DatabaseConnectionError as e:
            raise DatabaseConnectionError(
                f"Failed to initialize database with params {connection_params}: {str(e)}"
            ) from e
```

### 2. Error Recovery Patterns

```python
class ResilientDatabaseConnection:
    def __init__(self, engine_type: TargetDatabaseEngine):
        self.engine_type = engine_type
        self.connection = None
        
    def ensure_connection(self):
        if not self.connection:
            try:
                self.connection = DatabaseConnection(self.engine_type)
                self.connection.connect_to_database()
            except DatabaseConnectionError:
                self.connection = None
                raise
```

### 3. Transaction Management

```python
class TransactionManager:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def execute_transaction(self, queries: List[str]):
        try:
            for query in queries:
                self.db.execute_sql_to_panda_dataframe(query)
        except DatabaseConnectionError:
            logging.error("Transaction failed, rolling back")
            raise
```

## Practical Examples

### 1. Production Database Operations

```python
class ProductionDatabase:
    def __init__(self):
        try:
            self.db = DatabaseConnection(
                TargetDatabaseEngine.POSTGRESQL,
                TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
            ).change_default_username_and_password(False) \
             .finalization_of_connection_parameters(
                host="prod.example.com",
                port=5432,
                database="production_db"
             ).connect_to_database()
        except DatabaseConnectionError as e:
            logging.critical(f"Failed to connect to production database: {e}")
            sys.exit(1)
```

### 2. Data Migration Tool

```python
class DataMigrationTool:
    def migrate_data(self, source_db, target_db):
        try:
            data = source_db.execute_sql_to_panda_dataframe(
                "SELECT * FROM source_table"
            )
            # Process data...
            target_db.execute_sql_to_panda_dataframe(
                "INSERT INTO target_table..."
            )
        except DatabaseConnectionError as e:
            logging.error(f"Migration failed: {e}")
            self.notify_admin(str(e))
            raise
```

### 3. Health Check System

```python
class DatabaseHealthCheck:
    def check_connection(self, connection_params: dict) -> bool:
        try:
            db = DatabaseConnection(
                TargetDatabaseEngine.MSSQL
            ).finalization_of_connection_parameters(**connection_params)
            db.execute_sql_to_prettytable("SELECT 1", is_print=False)
            return True
        except DatabaseConnectionError:
            return False
```

### 4. Multi-Database Operations

```python
class MultiDatabaseManager:
    def __init__(self, configs: List[dict]):
        self.connections = {}
        for config in configs:
            try:
                connection = DatabaseConnection(
                    config['engine_type']
                ).finalization_of_connection_parameters(**config['params'])
                self.connections[config['name']] = connection
            except DatabaseConnectionError as e:
                logging.error(f"Failed to initialize {config['name']}: {e}")
```

Would you like me to expand on any specific aspect or add more examples?