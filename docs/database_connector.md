# 🔌 DatabaseConnector Documentation

## Table of Contents

1. [🎯 Overview](#overview)
2. [🔗 Dependencies](#dependencies)
3. [🏗️ Class Architecture](#architecture)
4. [🛠️ Implementation Details](#implementation)
   - [Initialization](#initialization)
   - [Core Methods](#core-methods)
   - [Query Operations](#query-operations)
   - [CRUD Operations](#crud-operations)
   - [Transaction Management](#transactions)
5. [📊 Usage Examples](#usage)
6. [⚠️ Error Handling](#error-handling)
7. [🔍 Best Practices](#best-practices)

## 🎯 Overview <a name="overview"></a>

[↑ Back to Top](#table-of-contents)

The `DatabaseConnector` class implements the `BaseDatabaseConnector` abstract base class, providing a concrete implementation for database operations with support for multiple database engines. It uses a fluent interface pattern for method chaining and configuration.

## 🔗 Dependencies <a name="dependencies"></a>

[↑ Back to Top](#table-of-contents)

```python
from getpass import getpass
import logging
import importlib
import pandas as pd
from prettytable import PrettyTable
from pathlib import Path
from dotenv import load_dotenv
from .db_templates import (
    MSSQL, MYSQL, POSTGRESQL, PSYCOPG2, SQLITE3, DUCKDB as template
)
from .db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine, 
    TargetDatabaseConnectionStringOption
)
```

## 🏗️ Class Architecture <a name="architecture"></a>

[↑ Back to Top](#table-of-contents)

The DatabaseConnector extends BaseDatabaseConnector with specific engine support:

```python
class DatabaseConnector(BaseDatabaseConnector):
    """
    A fluent interface for database connections supporting multiple engines.
    Uses method chaining for configuration and execution.
    """
```

### Key Features:

- 🔐 Template-based engine configuration
- 📊 Fluent interface pattern
- 🔄 Method chaining support
- 🛡️ Error handling

## 🛠️ Implementation Details <a name="implementation"></a>

[↑ Back to Top](#table-of-contents)

### Initialization <a name="initialization"></a>

```python
def __init__(self, engine_type: TargetDatabaseEngine, 
             connect_option: TargetDatabaseConnectionStringOption):
    """Initialize database connection with specified engine and options."""
    super().__init__()
    self.target_database_engine_name = engine_type.name
    self.connect_option = connect_option
    self.engine_config = self._load_engine_config()
```

#### Engine Configuration

```python
def _load_engine_config(self) -> Dict[str, Any]:
    """Load engine-specific configuration."""
    try:
         return getattr(template, self.target_database_engine_name)
    except AttributeError as e:
        raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}") from e
```

### Core Methods <a name="core-methods"></a>

#### Connection Establishment

```python
def connect_to_database(self) -> 'DatabaseConnector':
    """Establish database connection."""
    try:
        module_name = self.engine_config['MODULE']
        module = importlib.import_module(module_name)
        self._connection = module.connect(self._connection_string)
        return self
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")
```

### Query Operations <a name="query-operations"></a>

#### DataFrame Queries

```python
def execute_sql_to_dataframe(self, sql: str, 
                           index_col: Optional[str] = None) -> pd.DataFrame:
    """Execute SQL and return results as DataFrame."""
    return super().execute_sql_to_dataframe(sql, index_col)
```

#### Formatted Table Output

```python
def execute_sql_to_prettytable(self, sql: str, 
                              is_print: bool = False) -> Optional[PrettyTable]:
    """Execute SQL and return/print results as PrettyTable."""
    return super().execute_sql_to_prettytable(sql, is_print)
```

### CRUD Operations <a name="crud-operations"></a>

All CRUD operations inherit from BaseDatabaseConnector with type-safe overrides:

#### Insert Operations

```python
def insert(self, table: str, data: Dict[str, Any]) -> int:
    """Insert single record and return inserted id."""
    return super().insert(table, data)

def bulk_insert(self, table: str, records: List[Dict[str, Any]]) -> None:
    """Insert multiple records."""
    super().bulk_insert(table, records)
```

#### Update and Delete

```python
def update(self, table: str, data: Dict[str, Any], 
           where: Dict[str, Any]) -> int:
    """Update records matching criteria."""
    return super().update(table, data, where)

def delete(self, table: str, where: Dict[str, Any]) -> int:
    """Delete records matching criteria."""
    return super().delete(table, where)
```

### Transaction Management <a name="transactions"></a>

```python
@contextmanager
def transaction(self):
    """Context manager for transaction handling."""
    with super().transaction():
        yield

def begin_transaction(self) -> None:
    """Start a new transaction."""
    super().begin_transaction()
```

## 📊 Usage Examples <a name="usage"></a>

[↑ Back to Top](#table-of-contents)

### Basic Connection

```python
with DatabaseConnector(
    TargetDatabaseEngine.MSSQL, 
    TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd
) as db:
    db.finalization_of_connection_parameters(
        timeout=30,
        encrypt=True
    ).connect_to_database()
```

### Data Operations

```python
# Insert Data
db.insert("users", {
    "name": "John Doe",
    "email": "john@example.com"
})

# Query with DataFrame
results_df = db.execute_sql_to_dataframe(
    "SELECT * FROM users WHERE name LIKE ?",
    index_col="id"
)

# Pretty Print Results
db.execute_sql_to_prettytable(
    "SELECT * FROM users ORDER BY name",
    is_print=True
)
```

## ⚠️ Error Handling <a name="error-handling"></a>

[↑ Back to Top](#table-of-contents)

```python
try:
    with db.transaction():
        db.insert("users", {"name": "John"})
except DatabaseError as e:
    print(f"Database operation failed: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    db.close()
```

## 🔍 Best Practices <a name="best-practices"></a>
[↑ Back to Top](#table-of-contents)

1. 🔐 **Resource Management**
   - Always use context managers (`with` statements)
   - Explicitly close connections when done

2. 🛡️ **Error Handling**
   - Catch specific exceptions first
   - Use appropriate exception types
   - Implement proper cleanup

3. 🔄 **Transaction Safety**
   - Use transaction context managers
   - Implement proper rollback mechanisms
   - Handle nested transactions carefully

4. 📊 **Query Efficiency**
   - Use parameterized queries
   - Implement batch operations for bulk data
   - Choose appropriate return types (DataFrame vs PrettyTable)

5. 🏗️ **Configuration**
   - Use environment variables for sensitive data
   - Implement proper template loading
   - Validate connection parameters

### Example Implementation Pattern:
```python
def process_data(db: DatabaseConnector, data: List[Dict[str, Any]]) -> None:
    with db.transaction():
        try:
            # Bulk insert with progress tracking
            db.bulk_insert("target_table", data)
            
            # Verify insertion
            result = db.execute_sql_to_dataframe(
                "SELECT COUNT(*) as count FROM target_table"
            )
            print(f"Inserted {result['count'][0]} records")
            
        except DatabaseError as e:
            print(f"Failed to process data: {e}")
            raise
```

[↑ Back to Top](#table-of-contents)