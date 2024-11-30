# 🔄 MultiDatabaseConnector Documentation

## Table of Contents
1. [🎯 Overview](#overview)
2. [🔗 Dependencies](#dependencies)
3. [🏗️ Architecture](#architecture)
   - [Data Classes](#data-classes)
   - [Core Class](#core-class)
4. [🛠️ Features](#features)
   - [Instance Management](#instance-management)
   - [Connection Handling](#connection-handling)
   - [Transaction Management](#transactions)
   - [Data Operations](#data-operations)
   - [Table Management](#table-management)
5. [📋 Advanced Features](#advanced-features)
6. [💡 Best Practices](#best-practices)
7. [📊 Examples](#examples)

## 🎯 Overview <a name="overview"></a>
[↑ Back to Top](#table-of-contents)

The `MultiDatabaseConnector` extends `BaseDatabaseConnector` to provide simultaneous connections to multiple databases, supporting different database engines with template-based configuration and management.

**Key Capabilities:**
- 🔌 Multiple concurrent database connections
- 🔄 Transaction management across databases
- 📋 Table copying between instances
- 🔍 Centralized logging and error handling

## 🔗 Dependencies <a name="dependencies"></a>
[↑ Back to Top](#table-of-contents)

```python
from getpass import getpass
import logging
from typing import Any, Dict, Optional, Union, List
from contextlib import contextmanager
import importlib
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
```

## 🏗️ Architecture <a name="architecture"></a>
[↑ Back to Top](#table-of-contents)

### Data Classes <a name="data-classes"></a>

```python
@dataclass
class DatabaseInstance:
    """Information about an attached database instance."""
    name: str
    engine_type: TargetDatabaseEngine
    connection_options: TargetDatabaseConnectionStringOption
    is_active: bool = True
    attached_at: datetime = datetime.now()
```

### Core Class <a name="core-class"></a>

```python
class MultiDatabaseConnector(BaseDatabaseConnector):
    def __init__(self):
        super().__init__()
        self.instances: Dict[str, DatabaseInstance] = {}
        self.connections: Dict[str, Any] = {}
        self.active_instance: Optional[str] = None
        self._transaction_instance: Optional[str] = None
        self._logger = logging.getLogger(__name__)
```

## 🛠️ Features <a name="features"></a>
[↑ Back to Top](#table-of-contents)

### Instance Management <a name="instance-management"></a>

#### Attaching Databases
```python
def attach(self, name: str, engine_type: TargetDatabaseEngine,
           connect_option: TargetDatabaseConnectionStringOption) -> 'MultiDatabaseConnector':
    """
    Attach a new database instance using template configuration.
    
    Example:
        connector.attach(
            "mssql_db",
            TargetDatabaseEngine.MSSQL,
            TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd
        )
    """
```

#### Switching Active Instance
```python
def use(self, instance_name: str) -> 'MultiDatabaseConnector':
    """
    Switch active database instance.
    
    Example:
        connector.use("mysql_db")
    """
```

### Connection Handling <a name="connection-handling"></a>

#### Connection Creation
```python
def _create_database_connection(self) -> Any:
    """Create database connection using template configuration."""
```

#### Connection Management
```python
def close(self) -> None:
    """
    Close all database connections safely.
    
    Features:
    - Individual connection cleanup
    - Resource clearing
    - Logging of cleanup status
    """
```

### Transaction Management <a name="transactions"></a>

```python
@contextmanager
def transaction(self, instance_name: Optional[str] = None):
    """
    Transaction context manager with instance isolation.
    
    Example:
        with connector.transaction("mysql_db"):
            connector.execute("INSERT INTO ...")
    """
```

### Data Operations <a name="data-operations"></a>

#### Query Execution
```python
def query(self, query: str, instance_name: Optional[str] = None) -> pd.DataFrame:
    """
    Execute query on specified instance.
    
    Example:
        results = connector.query("SELECT * FROM users", "mysql_db")
    """
```

#### Batch Operations
```python
def executemany(self, query: str, parameters: List[Any],
                instance_name: Optional[str] = None) -> None:
    """
    Execute batch operations efficiently.
    
    Example:
        connector.executemany(
            "INSERT INTO users (name) VALUES (?)",
            [["John"], ["Jane"]]
        )
    """
```

### Table Management <a name="table-management"></a>

#### Cross-Database Table Copying
```python
def copy_table(self, source_instance: str, target_instance: str,
               table_name: str, batch_size: int = 1000) -> None:
    """
    Copy tables between database instances.
    
    Features:
    - Schema preservation
    - Batch processing
    - Progress tracking
    - Error handling
    
    Example:
        connector.copy_table("mssql_db", "mysql_db", "users")
    """
```

## 📋 Advanced Features <a name="advanced-features"></a>
[↑ Back to Top](#table-of-contents)

### 📊 Instance Information
```python
def get_instances_info(self) -> pd.DataFrame:
    """
    Get detailed information about all attached instances.
    
    Returns DataFrame with:
    - Instance names
    - Engine types
    - Active status
    - Connection timestamps
    """
```

### 🔍 Logging Integration
```python
self._logger.info(f"Successfully attached database: {name}")
self._logger.error(f"Query failed on instance {target}: {str(e)}")
self._logger.debug(f"Starting transaction on instance: {target_instance}")
```

## 💡 Best Practices <a name="best-practices"></a>
[↑ Back to Top](#table-of-contents)

1. 🔐 **Resource Management**
   ```python
   try:
       multi_db = MultiDatabaseConnector()
       # ... operations ...
   finally:
       multi_db.close()
   ```

2. 🔄 **Transaction Safety**
   ```python
   with multi_db.transaction():
       # All operations atomic
       multi_db.execute("...")
   ```

3. 📦 **Batch Processing**
   ```python
   # Use batch_size parameter for large operations
   multi_db.copy_table(
       "source_db", "target_db", "large_table",
       batch_size=5000
   )
   ```

## 📊 Examples <a name="examples"></a>
[↑ Back to Top](#table-of-contents)

### Complete Usage Example
```python
multi_db = MultiDatabaseConnector()

try:
    # Attach multiple databases
    multi_db.attach(
        "mssql_db",
        TargetDatabaseEngine.MSSQL,
        TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd
    ).attach(
        "mysql_db",
        TargetDatabaseEngine.MYSQL,
        TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd
    ).use("mssql_db")
    
    # Perform operations
    with multi_db.transaction():
        multi_db.execute("""
            CREATE TABLE example (
                id INT PRIMARY KEY,
                name VARCHAR(100)
            )
        """)
        
        multi_db.execute("""
            INSERT INTO example (id, name) 
            VALUES (1, 'Test Data')
        """)
    
    # Cross-database operations
    multi_db.copy_table("mssql_db", "mysql_db", "example")
    
except DatabaseError as e:
    print(f"Operation failed: {e}")
finally:
    multi_db.close()
```

### Error Handling Pattern
```python
try:
    with multi_db.transaction("source_db"):
        # Operations
        pass
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
finally:
    # Cleanup
    multi_db.close()
```

[↑ Back to Top](#table-of-contents)