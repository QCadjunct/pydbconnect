# 📚 BaseDatabaseConnector Documentation

## Table of Contents

1. [🎯 Overview](#overview)
2. [⚙️ Installation](#installation)
3. [🔧 Class Structure](#class-structure)
   - [Exceptions](#exceptions)
   - [Base Class](#base-class)
4. [🛠️ Core Features](#core-features)
   - [Connection Management](#connection-management)
   - [Query Operations](#query-operations)
   - [CRUD Operations](#crud-operations)
   - [Transaction Management](#transaction-management)
   - [Stored Procedures](#stored-procedures)
   - [Backup & Restore](#backup-restore)
5. [💻 Usage Examples](#usage-examples)
6. [📋 API Reference](#api-reference)
7. [🔍 Error Handling](#error-handling)

## 🎯 Overview <a name="overview"></a>

[↑ Back to Top](#table-of-contents)

The `BaseDatabaseConnector` is an abstract base class that provides a standardized interface for database connections and operations. It implements a template pattern for database engine configuration and supports various database operations through a fluent interface.

**Key Features:**

- Template-based engine configuration 
- Secure credential management
- Comprehensive CRUD operations
- Transaction support
- Stored procedure execution
- Backup and restore capabilities

## ⚙️ Installation <a name="installation"></a>

[↑ Back to Top](#table-of-contents)

```bash
pip install pandas python-dotenv prettytable
```

Required dependencies:

- pandas
- python-dotenv
- prettytable

## 🔧 Class Structure <a name="class-structure"></a>

[↑ Back to Top](#table-of-contents)

### Exceptions <a name="exceptions"></a>

```python
class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class ConnectionError(DatabaseError):
    """Exception raised for connection failures"""
    pass

class CredentialsError(DatabaseError):
    """Exception raised for credential issues"""
    pass
```

### Base Class <a name="base-class"></a>

```python
class BaseDatabaseConnector(ABC):
    def __init__(self):
        self.target_database_engine_name = None
        self.connect_option = None
        self.engine_config = None
        self._connection = None
        self._credentials = {'username': None, 'password': None, 'is_default': True}
        self._connection_string = None
```

## 🛠️ Core Features <a name="core-features"></a>

[↑ Back to Top](#table-of-contents)

### Connection Management <a name="connection-management"></a>

#### 🔐 Credential Management

```python
def change_default_username_and_password(self, show_password: bool = False) -> 'BaseDatabaseConnector':
    """
    Change database credentials interactively.
    
    Args:
        show_password (bool): Whether to show password during input
        
    Returns:
        Self for method chaining
    """
```

#### 🔌 Connection Parameters

```python
def finalization_of_connection_parameters(self, **params) -> 'BaseDatabaseConnector':
    """
    Finalize connection parameters with custom values.
    
    Args:
        **params: Custom connection parameters
        
    Returns:
        Self for method chaining
    """
```

### Query Operations <a name="query-operations"></a>

#### 📊 DataFrame Queries

```python
def execute_sql_to_dataframe(self, sql: str, index_col: Optional[str] = None) -> pd.DataFrame:
    """
    Execute SQL and return results as DataFrame.
    
    Args:
        sql: SQL query string
        index_col: Column to set as index
        
    Returns:
        pandas DataFrame with query results
    """
```

#### 📋 PrettyTable Output

```python
def execute_sql_to_prettytable(self, sql: str, is_print: bool = False) -> Optional[PrettyTable]:
    """
    Execute SQL and return/print results as PrettyTable.
    
    Args:
        sql: SQL query string
        is_print: Whether to print the table
        
    Returns:
        PrettyTable object or None if printed
    """
```

### CRUD Operations <a name="crud-operations"></a>

#### ➕ Insert

```python
def insert(self, table: str, data: Dict[str, Any]) -> int:
    """
    Insert single record and return inserted id.
    
    Args:
        table: Target table name
        data: Dictionary of column-value pairs
        
    Returns:
        ID of inserted record
    """
```

#### 🔄 Update

```python
def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
    """
    Update records matching criteria.
    
    Args:
        table: Target table name
        data: Dictionary of column-value pairs to update
        where: Dictionary of column-value pairs for WHERE clause
        
    Returns:
        Number of affected rows
    """
```

### Transaction Management <a name="transaction-management"></a>

#### 📦 Transaction Context

```python
@contextmanager
def transaction(self):
    """
    Context manager for transaction handling.
    
    Usage:
        with connector.transaction():
            connector.execute(...)
    """
```

#### 🔖 Savepoints

```python
def savepoint(self, name: str) -> None:
    """
    Create a savepoint in current transaction.
    
    Args:
        name: Savepoint identifier
    """
```

### Stored Procedures <a name="stored-procedures"></a>

```python
def execute_procedure(self, name: str, params: Optional[List[Any]] = None) -> Optional[List[Any]]:
    """
    Execute stored procedure with optional parameters.
    
    Args:
        name: Procedure name
        params: List of parameters
        
    Returns:
        Procedure results if available
    """
```

### Backup & Restore <a name="backup-restore"></a>

```python
def backup_database(self, path: str) -> None:
    """
    Backup database to specified path.
    
    Args:
        path: Backup file destination
    """
```

## 💻 Usage Examples <a name="usage-examples"></a>

[↑ Back to Top](#table-of-contents)

### Basic Usage

```python
class MyDatabaseConnector(BaseDatabaseConnector):
    def _load_engine_config(self) -> Dict[str, Any]:
        return {
            'MODULE': 'pyodbc',
            'DSN_TEMPLATE': 'DRIVER={{SQL Server}};SERVER={server};DATABASE={database}',
            'REQUIRES_CREDENTIALS': True,
            'DEFAULT_PARAMETERS': {'timeout': 30}
        }

# Using the connector
with MyDatabaseConnector() as db:
    db.change_default_username_and_password()
    db.finalization_of_connection_parameters(server='localhost')
    db.connect_to_database()
    
    results = db.execute_sql_to_dataframe("SELECT * FROM users")
```

### Transaction Example

```python
with connector.transaction():
    connector.insert("users", {"name": "John", "email": "john@example.com"})
    connector.update("users", 
                    {"status": "active"}, 
                    {"email": "john@example.com"})
```

## 📋 API Reference <a name="api-reference"></a>

[↑ Back to Top](#table-of-contents)

### Connection Methods

- `change_default_username_and_password(show_password: bool = False) -> BaseDatabaseConnector`
- `finalization_of_connection_parameters(**params) -> BaseDatabaseConnector`
- `connect_to_database() -> BaseDatabaseConnector`
- `close() -> None`

### Query Methods

- `execute_sql_to_dataframe(sql: str, index_col: Optional[str] = None) -> pd.DataFrame`
- `execute_sql_to_prettytable(sql: str, is_print: bool = False) -> Optional[PrettyTable]`

### CRUD Methods

- `insert(table: str, data: Dict[str, Any]) -> int`
- `bulk_insert(table: str, records: List[Dict[str, Any]]) -> None`
- `update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int`
- `delete(table: str, where: Dict[str, Any]) -> int`
- `select(table: str, columns: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]`

## 🔍 Error Handling <a name="error-handling"></a>

[↑ Back to Top](#table-of-contents)

The connector uses a hierarchical exception system:

- `DatabaseError`: Base exception for all database operations
- `ConnectionError`: Specific to connection failures
- `CredentialsError`: Related to authentication issues

Example error handling:

```python
try:
    with connector.transaction():
        connector.execute("INSERT INTO users...")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except CredentialsError as e:
    print(f"Authentication failed: {e}")
except DatabaseError as e:
    print(f"Database operation failed: {e}")
```

[↑ Back to Top](#table-of-contents)