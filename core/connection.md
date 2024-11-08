# Database Connection Documentation

## Overview
The `DatabaseConnection` class provides a fluent interface for database operations across different database engines. It manages connections, transactions, and data operations with a focus on type safety and proper resource management.

## Key Features
- Fluent interface design pattern
- Support for multiple database engines
- DataFrame operations integration
- Transaction management
- Bulk operations support
- Connection state management

## Basic Usage

### 1. Establishing a Connection
```python
# Basic connection
db = DatabaseConnection("MSSQL") \
    .with_credentials("username", "password") \
    .connect()

# Connection with DSN
db = DatabaseConnection("POSTGRESQL", use_dsn=True) \
    .with_credentials_from_env() \
    .connect()

# Connection with custom parameters
db = DatabaseConnection("MYSQL") \
    .with_credentials("user", "pass") \
    .with_params(
        PORT_NUMBER=3306,
        DATABASE_NAME="mydb"
    ) \
    .connect()
```

### 2. Query Execution
```python
# Simple query
results = db.execute_sql_to_panda_dataframe(
    "SELECT * FROM users WHERE status = ?",
    params=("active",)
)

# Query with transformations
results = db.execute_sql_to_panda_dataframe(
    "SELECT * FROM metrics",
    return_dataframe=False
) \
.transform_dataframe("standardize", columns=["value"]) \
.transform_dataframe(lambda df: df.assign(
    log_value=np.log(df["value"])
))
```

### 3. Transaction Management
```python
# Using context manager
with db.transaction():
    db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("John", "john@example.com")
    )
    db.execute(
        "UPDATE user_counts SET total = total + 1"
    )

# Manual transaction management
db.begin_transaction()
try:
    db.execute("INSERT INTO logs VALUES (?)", ("test",))
    db.commit()
except Exception:
    db.rollback()
    raise
```

### 4. Bulk Operations
```python
# Bulk insert
df = pd.DataFrame({
    "name": ["John", "Jane"],
    "age": [25, 30]
})

db.bulk_insert("users", df, batch_size=1000)
```

## API Reference

### Constructor
```python
DatabaseConnection(engine_type: str, use_dsn: bool = False)
```
- `engine_type`: Database engine type (e.g., "MSSQL", "POSTGRESQL")
- `use_dsn`: Whether to use DSN for connection

### Connection Methods
```python
with_credentials(username: str, password: str) -> DatabaseConnection
with_credentials_from_env() -> DatabaseConnection
with_params(**params: Any) -> DatabaseConnection
connect() -> DatabaseConnection
close() -> None
```

### Query Methods
```python
execute(query: str, params: Optional[tuple] = None) -> Any
execute_sql_to_panda_dataframe(
    sql_command: str,
    index_column: Optional[str] = None,
    return_dataframe: bool = True,
    store_history: bool = False,
    **kwargs: Any
) -> Union[DatabaseConnection, pd.DataFrame]
```

### DataFrame Operations
```python
transform_dataframe(
    transformation: Union[Callable[[pd.DataFrame], pd.DataFrame], str],
    columns: Optional[List[str]] = None,
    **kwargs: Any
) -> DatabaseConnection
```

### Transaction Methods
```python
@contextmanager
transaction()
begin_transaction() -> DatabaseConnection
commit() -> DatabaseConnection
rollback() -> DatabaseConnection
```

### Bulk Operations
```python
bulk_insert(
    table: str,
    df: pd.DataFrame,
    batch_size: int = 1000
) -> DatabaseConnection
execute_many(
    query: str,
    params_list: List[tuple]
) -> DatabaseConnection
```

### Properties
```python
@property
is_connected() -> bool
@property
in_transaction() -> bool
```

## Error Handling

The class uses a hierarchy of custom exceptions:
- `DatabaseError`: Base exception class
- `DatabaseConnectionError`: Connection-related errors
- `DatabaseOperationError`: Query execution errors
- `ValidationError`: Parameter validation errors

Example error handling:
```python
try:
    db = DatabaseConnection("MSSQL") \
        .with_credentials("user", "pass") \
        .connect()
    results = db.execute_sql_to_panda_dataframe("SELECT * FROM users")
except DatabaseConnectionError as e:
    print(f"Connection failed: {e}")
except DatabaseOperationError as e:
    print(f"Query failed: {e}")
finally:
    db.close()
```

## Best Practices

1. **Resource Management**
   - Always use context managers for transactions
   - Close connections when done
   - Use `with` statements for automatic cleanup

2. **Performance**
   - Use bulk operations for large datasets
   - Set appropriate batch sizes
   - Monitor transaction levels

3. **Error Handling**
   - Catch specific exceptions
   - Properly handle rollbacks
   - Validate parameters before execution

4. **DataFrame Operations**
   - Store history when needed
   - Use built-in transformations
   - Chain operations efficiently

5. **Configuration**
   - Use environment variables for credentials
   - Validate all required parameters
   - Set appropriate timeouts