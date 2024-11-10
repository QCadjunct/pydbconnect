# PyDBConnect Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [Connection Management](#connection-management)
5. [CRUD Operations](#crud-operations)
6. [Transaction Handling](#transaction-handling)
7. [Advanced Features](#advanced-features)
8. [API Reference](#api-reference)
9. [Error Handling](#error-handling)
10. [Best Practices & Patterns](#best-practices--patterns)

## Introduction

PyDBConnect is a powerful yet intuitive database interface library that simplifies database operations through a fluent, chainable API. It provides a consistent interface across multiple database engines while maintaining type safety and proper resource management.

### Key Features
- **Fluent Interface**: Chain methods for intuitive database operations
- **Type Safety**: Strong typing with runtime checks
- **Resource Management**: Automatic cleanup and connection pooling
- **Multi-Engine Support**: Works with MSSQL, PostgreSQL, MySQL, SQLite, and more
- **Transaction Support**: Both automatic and manual transaction management
- **Modern Python**: Leverages modern Python features and type hints

## Installation & Setup

### Basic Installation
```bash
# Basic installation
pip install pydbconnect

# With optional dependencies
pip install pydbconnect[all]  # Includes all database drivers
pip install pydbconnect[mssql]  # Just MSSQL support
pip install pydbconnect[postgres]  # Just PostgreSQL support
```

### Environment Configuration
Create a `.env` file for database credentials:
```env
# .env
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password
POSTGRES_USERNAME=pg_user
POSTGRES_PASSWORD=pg_pass
DEFAULT_KEY_MANAGEMENT_ENV_FILE=path/to/env/file

# Optional engine-specific settings
MSSQL_DEFAULT_PORT=1433
POSTGRES_DEFAULT_PORT=5432
```

## Core Concepts

### Database Engines
PyDBConnect supports multiple database engines through the `TargetDatabaseEngine` enum:

```python
from pydbconnect.enums import TargetDatabaseEngine

class TargetDatabaseEngine(Enum):
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"
```

### Connection String Options
Different connection methods are supported via `TargetDatabaseConnectionStringOption`:

```python
from pydbconnect.enums import TargetDatabaseConnectionStringOption

class TargetDatabaseConnectionStringOption(Enum):
    DefaultFormatAndDefaultUserPwd = 1    # Use default connection string and credentials
    DefaultFormatAndChangeUserPwd = 2     # Use default string, prompt for credentials
    CustomizeFormatAndDefaultUserPwd = 3  # Custom string, default credentials
    CustomizeFormatAndChangeUserPwd = 4   # Custom string and credentials
    Default_DSN_AndDefaultUserPwd = 5     # Use DSN with default credentials
    Default_DSN_AndChangeUserPwd = 6      # Use DSN, prompt for credentials
```

## Connection Management

### Basic Connection Patterns

#### 1. Simple Connection
```python
# Basic connection with default settings
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    database="Northwind"
).connect_to_database()
```

#### 2. Connection with Custom Credentials
```python
# Prompt for credentials
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).change_default_username_and_password(show_password=False) \
 .finalization_of_connection_parameters(
    host="db.example.com",
    port=5432,
    database="production"
) \
 .connect_to_database()
```

#### 3. DSN-Based Connection
```python
# Using DSN (Data Source Name)
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.Default_DSN_AndDefaultUserPwd
).finalization_of_connection_parameters(
    dsn="MyAppDSN"
).connect_to_database()
```

#### 4. Connection with Resource Management
```python
# Using context manager for automatic cleanup
with DatabaseConnection(
    TargetDatabaseEngine.MYSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
) as db:
    db.finalization_of_connection_parameters(
        host="localhost",
        port=3306,
        database="myapp"
    ).connect_to_database()
    
    # Connection automatically closes after context
```

### Connection Parameters

Each database engine supports specific connection parameters:

#### MSSQL Parameters
```python
mssql_params = {
    "host": "server.example.com",  # Server hostname
    "port": 1433,                  # Port number
    "database": "Northwind",       # Database name
    "trusted_connection": "yes",   # Windows authentication
    "timeout": 30,                 # Connection timeout
    "encrypt": "yes"              # Use encryption
}

db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL
).finalization_of_connection_parameters(**mssql_params)
```

#### PostgreSQL Parameters
```python
pg_params = {
    "host": "localhost",
    "port": 5432,
    "database": "myapp",
    "application_name": "MyApp",   # Application identifier
    "sslmode": "verify-full",     # SSL mode
    "connect_timeout": 10         # Connection timeout
}

db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL
).finalization_of_connection_parameters(**pg_params)
```

### Connection Pooling
PyDBConnect supports connection pooling for better performance:

```python
from pydbconnect.pool import DatabaseConnectionPool

# Create a connection pool
pool = DatabaseConnectionPool(
    engine_type=TargetDatabaseEngine.POSTGRESQL,
    min_connections=5,
    max_connections=20,
    connection_params={
        "host": "localhost",
        "database": "myapp"
    }
)

# Get connection from pool
with pool.get_connection() as db:
    results = db.select("users", where={"status": "active"})

# Connection automatically returns to pool
```

### Connection States
Connections have different states throughout their lifecycle:

```python
class DatabaseConnection:
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return bool(self._connection and not self._connection.closed)
    
    @property
    def is_in_transaction(self) -> bool:
        """Check if connection is in transaction."""
        return bool(self._transaction)
    
    def ping(self) -> bool:
        """Test if connection is alive."""
        try:
            with self._cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def reconnect(self) -> 'DatabaseConnection':
        """Reconnect if connection lost."""
        self.close()
        return self.connect_to_database()
```

### Connection Events
Monitor connection lifecycle events:

```python
from pydbconnect.events import ConnectionEventHandler

class MyConnectionHandler(ConnectionEventHandler):
    def on_connect(self, connection: DatabaseConnection):
        print(f"Connected to {connection.engine_type}")
    
    def on_disconnect(self, connection: DatabaseConnection):
        print("Connection closed")
    
    def on_error(self, connection: DatabaseConnection, error: Exception):
        print(f"Error occurred: {error}")

# Use custom handler
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    event_handler=MyConnectionHandler()
)
```

## CRUD Operations

### INSERT Operations

#### 1. Basic Insert
```python
# Single record insert
user_id = db.insert(
    table="users",
    data={
        "username": "john_doe",
        "email": "john@example.com",
        "created_at": "2024-01-01"
    }
)

print(f"Inserted user ID: {user_id}")
```

#### 2. Bulk Insert
```python
# Multiple records insert
users = [
    {
        "username": "user1",
        "email": "user1@example.com",
        "role": "user"
    },
    {
        "username": "user2",
        "email": "user2@example.com",
        "role": "admin"
    }
]

db.bulk_insert("users", users)

# With batch size for large datasets
def insert_large_dataset(db: DatabaseConnection, records: list, batch_size: int = 1000):
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        db.bulk_insert("users", batch)
```

#### 3. Insert with Returning Clause
```python
# PostgreSQL style RETURNING clause
created_user = db.insert(
    table="users",
    data={"username": "john", "email": "john@example.com"},
    returning=["id", "created_at"]
)
```

### SELECT Operations

#### 1. Basic Select
```python
# Select all records
all_users = db.select("users")

# Select specific columns
user_emails = db.select(
    table="users",
    columns=["username", "email"]
)

# Select with conditions
active_users = db.select(
    table="users",
    columns=["username", "email", "last_login"],
    where={"status": "active"}
)
```

#### 2. Advanced Queries
```python
# Complex SELECT using raw SQL
results = db.execute_sql_to_dataframe("""
    SELECT 
        u.username,
        COUNT(o.order_id) as total_orders,
        SUM(o.amount) as total_spent,
        MAX(o.order_date) as last_order
    FROM users u
    LEFT JOIN orders o ON u.user_id = o.user_id
    WHERE u.status = 'active'
    GROUP BY u.username
    HAVING COUNT(o.order_id) > 5
    ORDER BY total_spent DESC
    LIMIT 10
""")

# Using PrettyTable for formatted output
db.execute_sql_to_prettytable(
    "SELECT * FROM users WHERE role = 'admin'",
    is_print=True
)
```

#### 3. Parameterized Queries
```python
# Safe parameter handling
def get_user_orders(db: DatabaseConnection, user_id: int, start_date: str):
    return db.execute_sql_to_dataframe(
        """
        SELECT 
            order_id,
            order_date,
            amount
        FROM orders
        WHERE user_id = ? AND order_date >= ?
        """,
        params=[user_id, start_date]
    )
```

### UPDATE Operations

#### 1. Basic Update
```python
# Simple update
updated_count = db.update(
    table="users",
    data={"status": "inactive"},
    where={"last_login": "2023-01-01"}
)

print(f"Updated {updated_count} records")
```

#### 2. Conditional Updates
```python
# Complex update conditions
db.update(
    table="products",
    data={
        "price": 29.99,
        "updated_at": "2024-01-01",
        "status": "on_sale"
    },
    where={
        "category": "Electronics",
        "stock": 0,
        "price": 39.99
    }
)
```

#### 3. Batch Updates
```python
def batch_update_prices(db: DatabaseConnection, price_updates: list):
    with db.transaction():
        for update in price_updates:
            db.update(
                "products",
                data={"price": update["new_price"]},
                where={"product_id": update["product_id"]}
            )
```

### DELETE Operations

#### 1. Basic Delete
```python
# Simple delete
deleted_count = db.delete(
    table="users",
    where={"status": "inactive"}
)

print(f"Deleted {deleted_count} inactive users")
```

#### 2. Conditional Delete
```python
# Complex delete conditions
db.delete(
    table="orders",
    where={
        "status": "cancelled",
        "created_at": "2023-01-01",
        "amount": 0
    }
)
```

#### 3. Soft Delete Pattern
```python
def soft_delete_user(db: DatabaseConnection, user_id: int):
    with db.transaction():
        # Update user status
        db.update(
            "users",
            data={
                "status": "deleted",
                "deleted_at": datetime.now().isoformat()
            },
            where={"user_id": user_id}
        )
        
        # Archive user data
        user_data = db.select(
            "users",
            where={"user_id": user_id}
        )[0]
        
        db.insert(
            "users_archive",
            {**user_data, "archived_at": datetime.now().isoformat()}
        )
```

## Transaction Management

### 1. Automatic Transaction Management
```python
# Using context manager
with db.transaction():
    # Create order
    order_id = db.insert("orders", {
        "user_id": 1,
        "amount": 99.99
    })
    
    # Update inventory
    db.update(
        "products",
        data={"stock": -1},
        where={"product_id": 123}
    )
    
    # Create notification
    db.insert("notifications", {
        "user_id": 1,
        "message": f"Order {order_id} created"
    })
```

### 2. Manual Transaction Control
```python
# Manual transaction handling
def process_order(db: DatabaseConnection, order_data: dict):
    db.begin_transaction()
    try:
        # Create order
        order_id = db.insert("orders", order_data)
        
        # Create savepoint
        db.savepoint("after_order_create")
        
        # Process payment
        payment_result = process_payment(order_data["amount"])
        if not payment_result.success:
            db.rollback_to("after_order_create")
            db.update(
                "orders",
                data={"status": "payment_failed"},
                where={"order_id": order_id}
            )
        
        db.commit()
        return order_id
    except Exception as e:
        db.rollback()
        raise OrderProcessingError(f"Failed to process order: {e}")
```

### 3. Nested Transactions
```python
def process_batch_orders(db: DatabaseConnection, orders: list):
    with db.transaction():  # Outer transaction
        for order in orders:
            try:
                with db.transaction():  # Nested transaction
                    process_single_order(db, order)
            except Exception as e:
                logging.error(f"Failed to process order: {e}")
                # Continue with next order, outer transaction maintains integrity
```

## Advanced Features

### 1. Stored Procedures
```python
# Execute stored procedure
def generate_report(db: DatabaseConnection, start_date: str, end_date: str):
    results = db.execute_procedure(
        "generate_sales_report",
        params=[start_date, end_date]
    )
    
    if results:
        summary, details = results
        return {
            "summary": pd.DataFrame(summary),
            "details": pd.DataFrame(details)
        }
```

### 2. Backup and Restore
```python
def backup_routine(db: DatabaseConnection):
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"/backups/db_{timestamp}.bak"
    
    try:
        # Create backup
        db.backup_database(backup_path)
        
        # Verify backup
        db.execute_sql_to_prettytable(
            "RESTORE VERIFYONLY FROM DISK = ?",
            params=[backup_path]
        )
        
        return backup_path
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        raise
```

### 3. Bulk Operations
```python
# Bulk data loading
def load_csv_data(db: DatabaseConnection, csv_path: str, table: str):
    df = pd.read_csv(csv_path)
    records = df.to_dict('records')
    
    with db.transaction():
        # Clear existing data
        db.delete(table, where={})
        
        # Bulk insert with progress
        total = len(records)
        for i in range(0, total, 1000):
            batch = records[i:i + 1000]
            db.bulk_insert(table, batch)
            print(f"Processed {min(i + 1000, total)}/{total} records")
```


## Error Handling & Logging

### 1. Exception Hierarchy
```python
from pydbconnect.exceptions import (
    DatabaseError,
    ConnectionError,
    CredentialsError,
    TransactionError,
    QueryError
)

class CustomErrorHandler:
    def handle_database_error(self, db: DatabaseConnection, error: Exception):
        if isinstance(error, ConnectionError):
            # Handle connection issues
            logging.error(f"Connection failed: {error}")
            self.attempt_reconnect(db)
            
        elif isinstance(error, CredentialsError):
            # Handle credential issues
            logging.error(f"Authentication failed: {error}")
            self.request_new_credentials(db)
            
        elif isinstance(error, TransactionError):
            # Handle transaction failures
            logging.error(f"Transaction failed: {error}")
            self.rollback_and_cleanup(db)
            
        else:
            # Handle general database errors
            logging.error(f"Database operation failed: {error}")
            raise
```

### 2. Comprehensive Error Handling
```python
class DatabaseOperations:
    def __init__(self, connection_params: dict):
        self.connection_params = connection_params
        self.error_handler = CustomErrorHandler()
        
    def execute_with_retry(self, operation: callable, max_retries: int = 3):
        retries = 0
        while retries < max_retries:
            try:
                with DatabaseConnection(
                    TargetDatabaseEngine.POSTGRESQL,
                    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
                ) as db:
                    db.finalization_of_connection_parameters(**self.connection_params)
                    db.connect_to_database()
                    return operation(db)
                    
            except ConnectionError as e:
                retries += 1
                if retries == max_retries:
                    raise
                logging.warning(f"Retry {retries}/{max_retries} after error: {e}")
                time.sleep(2 ** retries)  # Exponential backoff
                
            except DatabaseError as e:
                self.error_handler.handle_database_error(db, e)
                raise
```

### 3. Logging Integration
```python
import logging
from datetime import datetime

class DatabaseLogger:
    def __init__(self, log_file: str = "database.log"):
        self.logger = logging.getLogger("pydbconnect")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(fh)
        
    def log_operation(self, operation: str, details: dict):
        self.logger.info(f"Operation: {operation}, Details: {details}")
        
    def log_error(self, error: Exception, context: dict):
        self.logger.error(f"Error: {error}, Context: {context}")

# Usage with database operations
class LoggedDatabaseConnection(DatabaseConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = DatabaseLogger()
        
    def execute_sql_to_dataframe(self, sql: str, *args, **kwargs):
        try:
            start_time = datetime.now()
            result = super().execute_sql_to_dataframe(sql, *args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.log_operation("query_execution", {
                "sql": sql,
                "execution_time": execution_time,
                "rows_returned": len(result)
            })
            
            return result
        except Exception as e:
            self.logger.log_error(e, {"sql": sql, "args": args})
            raise
```

## Best Practices & Patterns

### 1. Repository Pattern
```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    status: str

class UserRepository:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        
    def create(self, user: User) -> int:
        return self.db.insert("users", {
            "username": user.username,
            "email": user.email,
            "status": user.status
        })
        
    def find_by_id(self, user_id: int) -> Optional[User]:
        results = self.db.select(
            "users",
            where={"id": user_id}
        )
        return User(**results[0]) if results else None
        
    def find_active_users(self) -> List[User]:
        results = self.db.select(
            "users",
            where={"status": "active"}
        )
        return [User(**row) for row in results]
        
    def update(self, user: User) -> bool:
        if not user.id:
            raise ValueError("User ID is required for update")
            
        updated = self.db.update(
            "users",
            data={
                "username": user.username,
                "email": user.email,
                "status": user.status
            },
            where={"id": user.id}
        )
        return updated > 0
```

### 2. Unit of Work Pattern
```python
class UnitOfWork:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.users = UserRepository(db)
        self.orders = OrderRepository(db)
        
    def __enter__(self):
        self.db.begin_transaction()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
            
    def complete(self):
        self.db.commit()

# Usage
def create_user_with_order(db: DatabaseConnection, user_data: dict, order_data: dict):
    with UnitOfWork(db) as uow:
        # Create user
        user = User(**user_data)
        user_id = uow.users.create(user)
        
        # Create order
        order_data['user_id'] = user_id
        order = Order(**order_data)
        uow.orders.create(order)
```

### 3. Query Builder Pattern
```python
class QueryBuilder:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.query = ""
        self.params = []
        
    def select(self, *columns):
        self.query = f"SELECT {','.join(columns)}"
        return self
        
    def from_table(self, table):
        self.query += f" FROM {table}"
        return self
        
    def where(self, **conditions):
        if conditions:
            clauses = []
            for key, value in conditions.items():
                clauses.append(f"{key} = ?")
                self.params.append(value)
            self.query += f" WHERE {' AND '.join(clauses)}"
        return self
        
    def order_by(self, *columns):
        if columns:
            self.query += f" ORDER BY {','.join(columns)}"
        return self
        
    def execute(self):
        return self.db.execute_sql_to_dataframe(
            self.query,
            params=self.params
        )

# Usage
query = (QueryBuilder(db)
         .select("id", "username", "email")
         .from_table("users")
         .where(status="active")
         .order_by("username"))
results = query.execute()
```

### 4. Connection Pool Pattern
```python
from queue import Queue
from threading import Lock
import threading

class ConnectionPool:
    def __init__(self, size: int, **connection_params):
        self.size = size
        self.connection_params = connection_params
        self.pool = Queue(maxsize=size)
        self.lock = Lock()
        self._fill_pool()
        
    def _fill_pool(self):
        for _ in range(self.size):
            connection = DatabaseConnection(
                TargetDatabaseEngine.POSTGRESQL,
                TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
            )
            connection.finalization_of_connection_parameters(**self.connection_params)
            connection.connect_to_database()
            self.pool.put(connection)
            
    def get_connection(self):
        return self.pool.get()
        
    def return_connection(self, connection):
        if connection.ping():  # Check if connection is still valid
            self.pool.put(connection)
        else:
            # Replace dead connection
            self._replace_connection()
            
    def _replace_connection(self):
        with self.lock:
            connection = DatabaseConnection(
                TargetDatabaseEngine.POSTGRESQL,
                TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
            )
            connection.finalization_of_connection_parameters(**self.connection_params)
            connection.connect_to_database()
            self.pool.put(connection)

# Usage with context manager
@contextmanager
def pooled_connection(pool: ConnectionPool):
    connection = pool.get_connection()
    try:
        yield connection
    finally:
        pool.return_connection(connection)

# Example usage
pool = ConnectionPool(5, host="localhost", database="myapp")

def process_user(user_id: int):
    with pooled_connection(pool) as db:
        return db.select("users", where={"id": user_id})
```

# PyDBConnect Documentation (Part 4)

## Advanced Usage Scenarios

### 1. Event-Driven Database Operations
```python
from typing import Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DatabaseEvent:
    type: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()

class EventDrivenDatabase:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.event_handlers: Dict[str, List[Callable]] = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def emit_event(self, event: DatabaseEvent):
        # Log event
        self.db.insert("event_log", {
            "type": event.type,
            "data": str(event.data),
            "timestamp": event.timestamp.isoformat()
        })
        
        # Execute handlers
        handlers = self.event_handlers.get(event.type, [])
        for handler in handlers:
            handler(event)

# Example Usage
class OrderSystem:
    def __init__(self, db: DatabaseConnection):
        self.event_db = EventDrivenDatabase(db)
        self._register_handlers()
        
    def _register_handlers(self):
        self.event_db.register_handler("order_created", self._handle_new_order)
        self.event_db.register_handler("order_shipped", self._update_inventory)
        
    def create_order(self, order_data: dict):
        with self.event_db.db.transaction():
            # Create order
            order_id = self.event_db.db.insert("orders", order_data)
            
            # Emit event
            self.event_db.emit_event(DatabaseEvent(
                type="order_created",
                data={"order_id": order_id, **order_data}
            ))
            
            return order_id
    
    def _handle_new_order(self, event: DatabaseEvent):
        # Send notification
        self._send_order_notification(event.data["order_id"])
        
    def _update_inventory(self, event: DatabaseEvent):
        # Update inventory levels
        self._adjust_inventory(event.data["products"])
```

### 2. Batch Processing with Progress Tracking
```python
from typing import Iterator
from tqdm import tqdm

class BatchProcessor:
    def __init__(self, db: DatabaseConnection, batch_size: int = 1000):
        self.db = db
        self.batch_size = batch_size
        
    def process_large_dataset(self, iterator: Iterator[Dict], table: str):
        total_processed = 0
        batch = []
        
        with tqdm(desc="Processing records") as pbar:
            for record in iterator:
                batch.append(record)
                
                if len(batch) >= self.batch_size:
                    self._process_batch(batch, table)
                    total_processed += len(batch)
                    pbar.update(len(batch))
                    batch = []
            
            # Process remaining records
            if batch:
                self._process_batch(batch, table)
                total_processed += len(batch)
                pbar.update(len(batch))
        
        return total_processed
    
    def _process_batch(self, batch: List[Dict], table: str):
        with self.db.transaction():
            self.db.bulk_insert(table, batch)

# Usage Example
def process_csv_file(db: DatabaseConnection, csv_path: str):
    def record_iterator():
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
    
    processor = BatchProcessor(db)
    total = processor.process_large_dataset(
        record_iterator(),
        table="imported_data"
    )
    print(f"Processed {total} records")
```

### 3. Real-time Data Synchronization
```python
import asyncio
from asyncio import Queue
from typing import Dict, Any

class DatabaseSynchronizer:
    def __init__(self, source_db: DatabaseConnection, target_db: DatabaseConnection):
        self.source = source_db
        self.target = target_db
        self.queue = Queue()
        self.running = False
        
    async def start(self):
        self.running = True
        await asyncio.gather(
            self._monitor_changes(),
            self._process_changes()
        )
        
    async def stop(self):
        self.running = False
        
    async def _monitor_changes(self):
        last_id = 0
        while self.running:
            changes = self.source.select(
                "change_log",
                where={"id > ": last_id},
                order_by=["id"]
            )
            
            for change in changes:
                await self.queue.put(change)
                last_id = change["id"]
            
            await asyncio.sleep(1)
            
    async def _process_changes(self):
        while self.running:
            change = await self.queue.get()
            try:
                await self._apply_change(change)
            except Exception as e:
                print(f"Failed to apply change {change['id']}: {e}")
            finally:
                self.queue.task_done()
                
    async def _apply_change(self, change: Dict[str, Any]):
        with self.target.transaction():
            if change["operation"] == "INSERT":
                self.target.insert(
                    change["table"],
                    change["data"]
                )
            elif change["operation"] == "UPDATE":
                self.target.update(
                    change["table"],
                    change["data"],
                    change["where"]
                )
            elif change["operation"] == "DELETE":
                self.target.delete(
                    change["table"],
                    change["where"]
                )
```

### 4. Database Migration System
```python
from typing import List
import importlib.util
import os

class Migration:
    def __init__(self, version: int, up_sql: str, down_sql: str):
        self.version = version
        self.up_sql = up_sql
        self.down_sql = down_sql

class MigrationManager:
    def __init__(self, db: DatabaseConnection, migrations_path: str):
        self.db = db
        self.migrations_path = migrations_path
        self._ensure_migration_table()
        
    def _ensure_migration_table(self):
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
    def load_migrations(self) -> List[Migration]:
        migrations = []
        for filename in os.listdir(self.migrations_path):
            if filename.endswith('.py'):
                path = os.path.join(self.migrations_path, filename)
                spec = importlib.util.spec_from_file_location("migration", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'Migration'):
                    migrations.append(module.Migration())
        
        return sorted(migrations, key=lambda m: m.version)
    
    def get_current_version(self) -> int:
        result = self.db.execute_sql_to_dataframe(
            "SELECT MAX(version) as version FROM migrations"
        )
        return result.iloc[0]['version'] if not result.empty else 0
    
    def migrate(self, target_version: Optional[int] = None):
        migrations = self.load_migrations()
        current_version = self.get_current_version()
        
        if target_version is None:
            target_version = migrations[-1].version if migrations else 0
        
        if target_version > current_version:
            # Migrate up
            for migration in migrations:
                if current_version < migration.version <= target_version:
                    self._apply_migration(migration, up=True)
        else:
            # Migrate down
            for migration in reversed(migrations):
                if target_version < migration.version <= current_version:
                    self._apply_migration(migration, up=False)
    
    def _apply_migration(self, migration: Migration, up: bool):
        with self.db.transaction():
            sql = migration.up_sql if up else migration.down_sql
            self.db.execute_sql_to_dataframe(sql)
            
            if up:
                self.db.insert("migrations", {"version": migration.version})
            else:
                self.db.delete("migrations", {"version": migration.version})

# Example Migration File (001_create_users.py)
class Migration:
    def __init__(self):
        self.version = 1
        self.up_sql = """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.down_sql = """
            DROP TABLE users;
        """

# Usage
manager = MigrationManager(db, "migrations")
manager.migrate()  # Migrate to latest version
manager.migrate(target_version=2)  # Migrate to specific version
```

# PyDBConnect Documentation (Part 5)

## Performance Optimization and Monitoring

### 1. Query Performance Monitoring
```python
from time import time
from functools import wraps
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class QueryMetrics:
    query: str
    execution_time: float
    rows_affected: int
    timestamp: float = time()
    trace_id: Optional[str] = None

class QueryPerformanceMonitor:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.metrics: List[QueryMetrics] = []
        self._setup_metrics_table()
        
    def _setup_metrics_table(self):
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS query_metrics (
                id SERIAL PRIMARY KEY,
                query TEXT,
                execution_time FLOAT,
                rows_affected INTEGER,
                timestamp TIMESTAMP,
                trace_id VARCHAR(50)
            )
        """)
    
    def monitor_query(self, trace_id: Optional[str] = None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time() - start_time
                    
                    # Record metrics
                    metrics = QueryMetrics(
                        query=kwargs.get('query', str(args[0]) if args else 'Unknown'),
                        execution_time=execution_time,
                        rows_affected=len(result) if hasattr(result, '__len__') else 0,
                        trace_id=trace_id
                    )
                    self._store_metrics(metrics)
                    
                    return result
                except Exception as e:
                    execution_time = time() - start_time
                    # Record failed query metrics
                    metrics = QueryMetrics(
                        query=str(e),
                        execution_time=execution_time,
                        rows_affected=0,
                        trace_id=trace_id
                    )
                    self._store_metrics(metrics)
                    raise
            return wrapper
        return decorator
    
    def _store_metrics(self, metrics: QueryMetrics):
        self.db.insert("query_metrics", {
            "query": metrics.query,
            "execution_time": metrics.execution_time,
            "rows_affected": metrics.rows_affected,
            "timestamp": datetime.fromtimestamp(metrics.timestamp),
            "trace_id": metrics.trace_id
        })
    
    def get_slow_queries(self, threshold_seconds: float = 1.0):
        return self.db.execute_sql_to_dataframe("""
            SELECT *
            FROM query_metrics
            WHERE execution_time > ?
            ORDER BY execution_time DESC
            LIMIT 10
        """, params=[threshold_seconds])

# Usage
class OptimizedDatabaseOperations:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.monitor = QueryPerformanceMonitor(db)
    
    @monitor.monitor_query(trace_id="user_search")
    def find_users(self, search_term: str):
        return self.db.execute_sql_to_dataframe("""
            SELECT *
            FROM users
            WHERE username LIKE ? OR email LIKE ?
        """, params=[f"%{search_term}%", f"%{search_term}%"])
```

### 2. Connection Pool Management with Metrics
```python
from threading import Lock
from queue import Queue, Empty
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ConnectionMetrics:
    created_at: datetime
    last_used: datetime
    total_queries: int
    total_errors: int
    avg_query_time: float

class MonitoredConnectionPool:
    def __init__(self, min_size: int = 5, max_size: int = 20, max_idle_time: int = 300):
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.pool: Queue = Queue(maxsize=max_size)
        self.metrics: Dict[str, ConnectionMetrics] = {}
        self.lock = Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        for _ in range(self.min_size):
            self._add_connection()
    
    def _add_connection(self):
        connection = DatabaseConnection(
            TargetDatabaseEngine.POSTGRESQL,
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        ).finalization_of_connection_parameters(
            host="localhost",
            database="myapp"
        ).connect_to_database()
        
        conn_id = id(connection)
        self.metrics[conn_id] = ConnectionMetrics(
            created_at=datetime.now(),
            last_used=datetime.now(),
            total_queries=0,
            total_errors=0,
            avg_query_time=0.0
        )
        
        self.pool.put(connection)
        return connection
    
    def get_connection(self) -> DatabaseConnection:
        try:
            connection = self.pool.get_nowait()
            metrics = self.metrics[id(connection)]
            
            # Check if connection is too old
            if datetime.now() - metrics.last_used > timedelta(seconds=self.max_idle_time):
                self._remove_connection(connection)
                return self._add_connection()
            
            return connection
        except Empty:
            if self.pool.qsize() < self.max_size:
                return self._add_connection()
            raise ConnectionError("Connection pool exhausted")
    
    def return_connection(self, connection: DatabaseConnection):
        if self._is_connection_healthy(connection):
            self.metrics[id(connection)].last_used = datetime.now()
            self.pool.put(connection)
        else:
            self._remove_connection(connection)
            self._add_connection()
    
    def _is_connection_healthy(self, connection: DatabaseConnection) -> bool:
        try:
            with connection._cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def _remove_connection(self, connection: DatabaseConnection):
        try:
            connection.close()
        finally:
            conn_id = id(connection)
            if conn_id in self.metrics:
                del self.metrics[conn_id]
    
    def get_pool_stats(self) -> dict:
        return {
            "active_connections": self.pool.qsize(),
            "total_connections": len(self.metrics),
            "avg_query_time": sum(m.avg_query_time for m in self.metrics.values()) / len(self.metrics) if self.metrics else 0,
            "total_queries": sum(m.total_queries for m in self.metrics.values()),
            "total_errors": sum(m.total_errors for m in self.metrics.values())
        }

class MonitoredDatabaseConnection:
    def __init__(self, pool: MonitoredConnectionPool):
        self.pool = pool
        self.connection = None
    
    def __enter__(self):
        self.connection = self.pool.get_connection()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Update error metrics
            metrics = self.pool.metrics[id(self.connection)]
            metrics.total_errors += 1
        
        self.pool.return_connection(self.connection)

# Usage
pool = MonitoredConnectionPool()

def execute_query():
    with MonitoredDatabaseConnection(pool) as db:
        start_time = time()
        try:
            result = db.execute_sql_to_dataframe("SELECT * FROM users")
            
            # Update metrics
            query_time = time() - start_time
            metrics = pool.metrics[id(db)]
            metrics.total_queries += 1
            metrics.avg_query_time = (
                (metrics.avg_query_time * (metrics.total_queries - 1) + query_time)
                / metrics.total_queries
            )
            
            return result
        except Exception as e:
            # Metrics are updated in __exit__
            raise
```

### 3. Query Optimization and Caching
```python
from functools import lru_cache
from hashlib import md5
from typing import Any, Optional
import pickle

class QueryCache:
    def __init__(self, db: DatabaseConnection, ttl: int = 300):
        self.db = db
        self.ttl = ttl
        self._setup_cache_table()
    
    def _setup_cache_table(self):
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS query_cache (
                key VARCHAR(32) PRIMARY KEY,
                data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
    
    def _generate_key(self, query: str, params: tuple) -> str:
        cache_key = f"{query}:{str(params)}"
        return md5(cache_key.encode()).hexdigest()
    
    def get(self, query: str, params: tuple = ()) -> Optional[Any]:
        key = self._generate_key(query, params)
        
        result = self.db.execute_sql_to_dataframe("""
            SELECT data
            FROM query_cache
            WHERE key = ?
              AND expires_at > CURRENT_TIMESTAMP
        """, params=[key])
        
        if not result.empty:
            return pickle.loads(result.iloc[0]['data'])
        return None
    
    def set(self, query: str, params: tuple, data: Any):
        key = self._generate_key(query, params)
        
        with self.db.transaction():
            # Remove old cache entry
            self.db.delete("query_cache", {"key": key})
            
            # Insert new cache entry
            self.db.insert("query_cache", {
                "key": key,
                "data": pickle.dumps(data),
                "expires_at": datetime.now() + timedelta(seconds=self.ttl)
            })
    
    def invalidate(self, pattern: str):
        self.db.delete(
            "query_cache",
            {"key LIKE": f"%{pattern}%"}
        )

class CachedDatabaseOperations:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.cache = QueryCache(db)
    
    def get_user_with_cache(self, user_id: int):
        query = "SELECT * FROM users WHERE id = ?"
        params = (user_id,)
        
        # Try cache first
        cached_result = self.cache.get(query, params)
        if cached_result is not None:
            return cached_result
        
        # Execute query and cache result
        result = self.db.execute_sql_to_dataframe(query, params=[user_id])
        if not result.empty:
            self.cache.set(query, params, result.to_dict('records')[0])
        return result

    def update_user_with_cache_invalidation(self, user_id: int, data: dict):
        with self.db.transaction():
            self.db.update("users", data, {"id": user_id})
            # Invalidate related cache entries
            self.cache.invalidate(f"users:{user_id}")
```

## Integration Patterns, Testing, and Deployment

### 1. Integration Patterns

#### FastAPI Integration
```python
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from contextlib import asynccontextmanager

class DatabaseIntegration:
    def __init__(self, connection_params: dict):
        self.connection_params = connection_params
        self.pool = MonitoredConnectionPool(
            min_size=5,
            max_size=20,
            **connection_params
        )

    @asynccontextmanager
    async def get_db(self) -> AsyncGenerator[DatabaseConnection, None]:
        db = None
        try:
            db = self.pool.get_connection()
            yield db
        finally:
            if db:
                self.pool.return_connection(db)

# FastAPI application setup
app = FastAPI()
db_integration = DatabaseIntegration({
    "host": "localhost",
    "database": "myapp"
})

# Dependency for database access
async def get_db():
    async with db_integration.get_db() as db:
        yield db

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: DatabaseConnection = Depends(get_db)):
    try:
        user = db.select("users", where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user[0]
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users")
async def create_user(user: dict, db: DatabaseConnection = Depends(get_db)):
    try:
        with db.transaction():
            user_id = db.insert("users", user)
            return {"id": user_id, **user}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### SQLAlchemy Integration
```python
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

class SQLAlchemyIntegration:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()

    def _create_engine(self):
        return create_engine(self.db._connection_string)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_raw_sql(self, query: str, params: dict = None):
        with self.session_scope() as session:
            return session.execute(query, params or {})

# Usage with SQLAlchemy models
from sqlalchemy import Table, Column, Integer, String

class SQLAlchemyRepository:
    def __init__(self, integration: SQLAlchemyIntegration):
        self.integration = integration
        self.users = Table('users', integration.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String),
            Column('email', String)
        )

    def find_user(self, user_id: int):
        query = self.users.select().where(self.users.c.id == user_id)
        with self.integration.session_scope() as session:
            return session.execute(query).first()
```

### 2. Testing Strategies

#### Unit Testing
```python
import pytest
from unittest.mock import Mock, patch
from typing import Generator

class TestDatabaseConnection:
    @pytest.fixture
    def mock_db(self) -> Generator[DatabaseConnection, None, None]:
        with patch('pydbconnect.connection.DatabaseConnection') as mock:
            connection = mock.return_value
            connection._connection = Mock()
            yield connection

    def test_insert(self, mock_db):
        # Arrange
        mock_db._cursor.return_value.__enter__.return_value.lastrowid = 1
        data = {"username": "test", "email": "test@example.com"}

        # Act
        result = mock_db.insert("users", data)

        # Assert
        assert result == 1
        mock_db._cursor.return_value.__enter__.return_value.execute.assert_called_once()

    def test_transaction_rollback(self, mock_db):
        # Arrange
        mock_db._connection.rollback = Mock()

        # Act
        with pytest.raises(Exception):
            with mock_db.transaction():
                raise Exception("Test error")

        # Assert
        mock_db._connection.rollback.assert_called_once()
```

#### Integration Testing
```python
import pytest
from typing import Generator
import tempfile
import os

class TestDatabaseIntegration:
    @pytest.fixture
    def test_db(self) -> Generator[DatabaseConnection, None, None]:
        # Create temporary SQLite database
        fd, path = tempfile.mkstemp()
        db = DatabaseConnection(
            TargetDatabaseEngine.SQLITE3,
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        ).finalization_of_connection_parameters(
            database=path
        ).connect_to_database()

        # Set up schema
        db.execute_sql_to_dataframe("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                email TEXT
            )
        """)

        yield db

        # Cleanup
        db.close()
        os.close(fd)
        os.unlink(path)

    def test_full_crud_cycle(self, test_db):
        # Insert
        user_id = test_db.insert("users", {
            "username": "test",
            "email": "test@example.com"
        })
        assert user_id > 0

        # Select
        user = test_db.select("users", where={"id": user_id})[0]
        assert user["username"] == "test"

        # Update
        updated = test_db.update(
            "users",
            {"username": "updated"},
            {"id": user_id}
        )
        assert updated == 1

        # Delete
        deleted = test_db.delete("users", {"id": user_id})
        assert deleted == 1
```

### 3. Deployment Considerations

#### Connection Configuration Management
```python
from typing import Dict
import yaml
import os

class DatabaseConfig:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.environment = os.getenv('ENVIRONMENT', 'development')

    def _load_config(self, path: str) -> Dict:
        with open(path) as f:
            return yaml.safe_load(f)

    def get_connection_params(self) -> Dict:
        base_config = self.config['database'][self.environment]
        
        # Override with environment variables if present
        env_mapping = {
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_NAME': 'database',
            'DB_USER': 'username',
            'DB_PASSWORD': 'password'
        }

        for env_var, config_key in env_mapping.items():
            if value := os.getenv(env_var):
                base_config[config_key] = value

        return base_config

class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pools: Dict[str, MonitoredConnectionPool] = {}

    def get_pool(self, name: str = 'default') -> MonitoredConnectionPool:
        if name not in self._pools:
            self._pools[name] = self._create_pool()
        return self._pools[name]

    def _create_pool(self) -> MonitoredConnectionPool:
        return MonitoredConnectionPool(
            **self.config.get_connection_params()
        )

    def cleanup(self):
        for pool in self._pools.values():
            pool.cleanup()
```

#### Health Checks and Monitoring
```python
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class HealthStatus:
    status: str
    details: Dict
    timestamp: datetime = datetime.now()

class DatabaseHealthCheck:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def check_health(self) -> HealthStatus:
        try:
            # Basic connectivity check
            with self.db._cursor() as cursor:
                start = datetime.now()
                cursor.execute("SELECT 1")
                response_time = (datetime.now() - start).total_seconds()

            # Get connection pool stats
            pool_stats = self.db.pool.get_pool_stats() if hasattr(self.db, 'pool') else {}

            return HealthStatus(
                status="healthy",
                details={
                    "response_time": response_time,
                    "pool_stats": pool_stats,
                    "connection_id": id(self.db._connection)
                }
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                details={"error": str(e)}
            )

    def export_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        status = self.check_health()
        metrics = []

        if status.status == "healthy":
            metrics.extend([
                f'database_response_time_seconds {status.details["response_time"]}',
                f'database_pool_size {status.details["pool_stats"].get("total_connections", 0)}',
                f'database_active_connections {status.details["pool_stats"].get("active_connections", 0)}',
                'database_health 1'
            ])
        else:
            metrics.append('database_health 0')

        return "\n".join(metrics)
```

# PyDBConnect Documentation (Part 7)

## Security Patterns, Data Validation, and Advanced Configuration

### 1. Security Patterns

#### Secure Credential Management
```python
from cryptography.fernet import Fernet
from typing import Optional
import base64
import os

class SecureCredentialManager:
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.getenv('DB_ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = self._generate_key()
        self.cipher = Fernet(self._get_or_generate_key())

    def _generate_key(self) -> str:
        """Generate new encryption key."""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

    def _get_or_generate_key(self) -> bytes:
        """Get existing key or generate new one."""
        try:
            return base64.urlsafe_b64decode(self.encryption_key)
        except:
            return base64.urlsafe_b64decode(self._generate_key())

    def encrypt_credentials(self, username: str, password: str) -> dict:
        """Encrypt database credentials."""
        return {
            'username': self.cipher.encrypt(username.encode()).decode(),
            'password': self.cipher.encrypt(password.encode()).decode()
        }

    def decrypt_credentials(self, encrypted_credentials: dict) -> dict:
        """Decrypt database credentials."""
        return {
            'username': self.cipher.decrypt(encrypted_credentials['username'].encode()).decode(),
            'password': self.cipher.decrypt(encrypted_credentials['password'].encode()).decode()
        }

class SecureDatabaseConnection(DatabaseConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.credential_manager = SecureCredentialManager()

    def set_credentials(self, username: str, password: str):
        """Securely store credentials."""
        encrypted = self.credential_manager.encrypt_credentials(username, password)
        self._credentials = encrypted

    def get_credentials(self) -> dict:
        """Retrieve decrypted credentials."""
        if not self._credentials:
            raise ValueError("No credentials set")
        return self.credential_manager.decrypt_credentials(self._credentials)

# Usage
db = SecureDatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
)
db.set_credentials("user", "password")  # Credentials are encrypted
```

#### SQL Injection Prevention
```python
from typing import Any, List, Dict
import re

class SQLSanitizer:
    DANGEROUS_PATTERNS = [
        r'--',           # SQL comments
        r';',           # Query separator
        r'\/\*|\*\/',   # Multi-line comments
        r'xp_',         # Extended stored procedures
        r'exec\s+',     # EXEC statements
        r'union\s+',    # UNION queries
    ]

    @classmethod
    def sanitize_value(cls, value: Any) -> Any:
        """Sanitize a single value."""
        if isinstance(value, str):
            # Remove dangerous SQL patterns
            sanitized = str(value)
            for pattern in cls.DANGEROUS_PATTERNS:
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            return sanitized
        return value

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all values in a dictionary."""
        return {k: cls.sanitize_value(v) for k, v in data.items()}

class SecureQueryBuilder:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.sanitizer = SQLSanitizer()

    def build_select(self, table: str, columns: List[str] = None, 
                    where: Dict[str, Any] = None) -> tuple:
        """Build secure SELECT query with parameters."""
        cols = ','.join(columns) if columns else '*'
        query = f"SELECT {cols} FROM {table}"
        params = []

        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(self.sanitizer.sanitize_value(value))
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        return query, params

    def execute_secure_query(self, query: str, params: List[Any] = None) -> Any:
        """Execute query with sanitized parameters."""
        sanitized_params = [self.sanitizer.sanitize_value(p) for p in (params or [])]
        return self.db.execute_sql_to_dataframe(query, params=sanitized_params)

# Usage
query_builder = SecureQueryBuilder(db)
query, params = query_builder.build_select(
    "users",
    columns=["id", "username"],
    where={"status": "active"; "DROP TABLE users;--"}  # Attempted SQL injection
)
results = query_builder.execute_secure_query(query, params)
```

### 2. Data Validation

#### Input Validation
```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum
import re

class ValidationError(Exception):
    pass

class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    EMAIL = "email"
    BOOLEAN = "boolean"

@dataclass
class FieldValidation:
    name: str
    data_type: DataType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class DataValidator:
    def __init__(self, validations: List[FieldValidation]):
        self.validations = {v.name: v for v in validations}

    def validate(self, data: dict) -> dict:
        """Validate and clean input data."""
        validated_data = {}

        for field_name, validation in self.validations.items():
            value = data.get(field_name)

            # Check required fields
            if validation.required and value is None:
                raise ValidationError(f"Field '{field_name}' is required")

            # Skip validation for optional empty fields
            if not validation.required and value is None:
                continue

            # Validate and convert value
            validated_data[field_name] = self._validate_field(value, validation)

        return validated_data

    def _validate_field(self, value: Any, validation: FieldValidation) -> Any:
        """Validate single field value."""
        if validation.data_type == DataType.STRING:
            return self._validate_string(value, validation)
        elif validation.data_type == DataType.INTEGER:
            return self._validate_integer(value, validation)
        elif validation.data_type == DataType.FLOAT:
            return self._validate_float(value, validation)
        elif validation.data_type == DataType.DATE:
            return self._validate_date(value, validation)
        elif validation.data_type == DataType.EMAIL:
            return self._validate_email(value, validation)
        elif validation.data_type == DataType.BOOLEAN:
            return self._validate_boolean(value)
        
        raise ValidationError(f"Unsupported data type: {validation.data_type}")

    def _validate_string(self, value: Any, validation: FieldValidation) -> str:
        value = str(value)
        
        if validation.min_length and len(value) < validation.min_length:
            raise ValidationError(
                f"Field '{validation.name}' must be at least {validation.min_length} characters"
            )
        
        if validation.max_length and len(value) > validation.max_length:
            raise ValidationError(
                f"Field '{validation.name}' must be at most {validation.max_length} characters"
            )
        
        if validation.pattern and not re.match(validation.pattern, value):
            raise ValidationError(
                f"Field '{validation.name}' does not match required pattern"
            )
        
        return value

    def _validate_email(self, value: Any, validation: FieldValidation) -> str:
        value = str(value)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            raise ValidationError(f"Field '{validation.name}' must be a valid email address")
        
        return value

class ValidatedDatabaseOperation:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.user_validator = DataValidator([
            FieldValidation("username", DataType.STRING, min_length=3, max_length=50),
            FieldValidation("email", DataType.EMAIL),
            FieldValidation("age", DataType.INTEGER, required=False, min_value=0),
            FieldValidation("status", DataType.STRING, pattern=r'^(active|inactive)$')
        ])

    def create_user(self, user_data: dict) -> int:
        """Create user with validated data."""
        validated_data = self.user_validator.validate(user_data)
        return self.db.insert("users", validated_data)

    def update_user(self, user_id: int, user_data: dict) -> bool:
        """Update user with validated data."""
        validated_data = self.user_validator.validate(user_data)
        return self.db.update("users", validated_data, {"id": user_id}) > 0

# Usage
db_ops = ValidatedDatabaseOperation(db)

# This will raise ValidationError for invalid email
try:
    db_ops.create_user({
        "username": "john_doe",
        "email": "invalid-email",
        "age": 25,
        "status": "active"
    })
except ValidationError as e:
    print(f"Validation failed: {e}")

# This will succeed
user_id = db_ops.create_user({
    "username": "john_doe",
    "email": "john@example.com",
    "age": 25,
    "status": "active"
})
```


## Advanced Configuration Management and Schema Migration

### 1. Advanced Configuration Management

#### Environment-Aware Configuration
```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import json
import os

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    timeout: int = 30

class ConfigurationManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.environment = Environment(os.getenv('APP_ENV', 'development'))
        self._config = self._load_configuration()
        self._secrets = self._load_secrets()

    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
            return config[self.environment.value]

    def _load_secrets(self) -> Dict[str, Any]:
        """Load secrets from environment or secrets file."""
        secrets_path = os.getenv('DB_SECRETS_PATH')
        if secrets_path and os.path.exists(secrets_path):
            with open(secrets_path) as f:
                return json.load(f)
        return {}

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration with merged secrets."""
        config = self._config['database'].copy()
        
        # Override with environment variables
        env_mapping = {
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_NAME': 'database',
            'DB_USER': 'username',
            'DB_PASS': 'password',
            'DB_POOL_SIZE': 'pool_size',
            'DB_MAX_OVERFLOW': 'max_overflow',
            'DB_TIMEOUT': 'timeout'
        }

        for env_var, config_key in env_mapping.items():
            if value := os.getenv(env_var):
                config[config_key] = value

        # Merge secrets
        config.update(self._secrets.get('database', {}))

        return DatabaseConfig(**config)

class DatabaseFactory:
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager

    def create_connection(self) -> DatabaseConnection:
        """Create database connection with configuration."""
        config = self.config_manager.get_database_config()
        
        db = DatabaseConnection(
            TargetDatabaseEngine.POSTGRESQL,
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        )
        
        if config.username and config.password:
            db._credentials = {
                'username': config.username,
                'password': config.password,
                'is_default': False
            }
        
        db.finalization_of_connection_parameters(
            host=config.host,
            port=config.port,
            database=config.database
        )
        
        return db.connect_to_database()

# Example configuration (config.yaml)
"""
development:
  database:
    host: localhost
    port: 5432
    database: myapp_dev
    pool_size: 5
    max_overflow: 10
    timeout: 30

staging:
  database:
    host: staging-db.example.com
    port: 5432
    database: myapp_staging
    pool_size: 10
    max_overflow: 20
    timeout: 60

production:
  database:
    host: prod-db.example.com
    port: 5432
    database: myapp_prod
    pool_size: 20
    max_overflow: 30
    timeout: 60
"""

# Usage
config_manager = ConfigurationManager('config.yaml')
db_factory = DatabaseFactory(config_manager)
db = db_factory.create_connection()
```

### 2. Schema Migration System

#### Version Control for Database Schemas
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Callable
import importlib.util
import os
import re

@dataclass
class Migration:
    version: int
    name: str
    up_sql: str
    down_sql: str
    applied_at: Optional[datetime] = None
    
    @property
    def is_applied(self) -> bool:
        return self.applied_at is not None

class MigrationManager:
    def __init__(self, db: DatabaseConnection, migrations_path: str):
        self.db = db
        self.migrations_path = migrations_path
        self._ensure_migration_table()

    def _ensure_migration_table(self):
        """Create migrations table if it doesn't exist."""
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _load_migration_files(self) -> List[Migration]:
        """Load migration files from directory."""
        migrations = []
        pattern = re.compile(r'V(\d+)__(.+)\.sql')
        
        for filename in sorted(os.listdir(self.migrations_path)):
            match = pattern.match(filename)
            if match:
                version = int(match.group(1))
                name = match.group(2)
                
                path = os.path.join(self.migrations_path, filename)
                with open(path) as f:
                    content = f.read()
                    
                # Split content into up and down migrations
                parts = content.split('-- Down')
                up_sql = parts[0].replace('-- Up', '').strip()
                down_sql = parts[1].strip() if len(parts) > 1 else ''
                
                migrations.append(Migration(
                    version=version,
                    name=name,
                    up_sql=up_sql,
                    down_sql=down_sql
                ))
                
        return sorted(migrations, key=lambda m: m.version)

    def get_applied_migrations(self) -> List[Migration]:
        """Get list of applied migrations."""
        results = self.db.execute_sql_to_dataframe("""
            SELECT version, name, applied_at
            FROM schema_migrations
            ORDER BY version
        """)
        
        return [Migration(
            version=row['version'],
            name=row['name'],
            up_sql='',
            down_sql='',
            applied_at=row['applied_at']
        ) for row in results.to_dict('records')]

    def migrate(self, target_version: Optional[int] = None):
        """Migrate database to target version or latest."""
        migrations = self._load_migration_files()
        applied = self.get_applied_migrations()
        applied_versions = {m.version for m in applied}
        
        if target_version is None and migrations:
            target_version = migrations[-1].version
            
        if target_version is None:
            return  # Nothing to do
            
        current_version = max(applied_versions) if applied_versions else 0
        
        # Determine direction and migrations to apply
        if target_version > current_version:
            # Migrate up
            to_apply = [
                m for m in migrations
                if current_version < m.version <= target_version
            ]
            self._apply_migrations(to_apply, up=True)
        else:
            # Migrate down
            to_apply = [
                m for m in migrations
                if target_version < m.version <= current_version
            ]
            self._apply_migrations(reversed(to_apply), up=False)

    def _apply_migrations(self, migrations: List[Migration], up: bool):
        """Apply migrations in transaction."""
        with self.db.transaction():
            for migration in migrations:
                print(f"{'Applying' if up else 'Reverting'} migration {migration.version}: {migration.name}")
                
                sql = migration.up_sql if up else migration.down_sql
                if not sql:
                    continue
                    
                self.db.execute_sql_to_dataframe(sql)
                
                if up:
                    self.db.insert('schema_migrations', {
                        'version': migration.version,
                        'name': migration.name
                    })
                else:
                    self.db.delete('schema_migrations', {
                        'version': migration.version
                    })

class MigrationCLI:
    def __init__(self, db: DatabaseConnection, migrations_path: str):
        self.manager = MigrationManager(db, migrations_path)

    def status(self):
        """Show migration status."""
        migrations = self.manager._load_migration_files()
        applied = self.manager.get_applied_migrations()
        applied_versions = {m.version for m in applied}
        
        print("\nMigration Status:")
        print("================")
        
        for migration in migrations:
            status = "Applied" if migration.version in applied_versions else "Pending"
            print(f"V{migration.version:03d} - {migration.name:30} [{status}]")

    def up(self, steps: Optional[int] = None):
        """Migrate up by number of steps or to latest."""
        migrations = self.manager._load_migration_files()
        if not steps:
            self.manager.migrate()
        else:
            applied = self.manager.get_applied_migrations()
            current = max(m.version for m in applied) if applied else 0
            
            # Find target version
            available = [m.version for m in migrations if m.version > current]
            if available and steps <= len(available):
                target = available[steps - 1]
                self.manager.migrate(target)

    def down(self, steps: int = 1):
        """Migrate down by number of steps."""
        applied = self.manager.get_applied_migrations()
        if not applied:
            print("No migrations to revert")
            return
            
        current = max(m.version for m in applied)
        available = [m.version for m in applied]
        available.sort(reverse=True)
        
        if steps <= len(available):
            target = available[steps - 1] - 1  # Go to version before target
            self.manager.migrate(target)

# Example Usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Tool')
    parser.add_argument('command', choices=['status', 'up', 'down'])
    parser.add_argument('--steps', type=int, help='Number of migrations to apply/revert')
    
    args = parser.parse_args()
    
    # Setup database connection
    db = DatabaseConnection(
        TargetDatabaseEngine.POSTGRESQL,
        TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
    ).finalization_of_connection_parameters(
        host="localhost",
        database="myapp"
    ).connect_to_database()
    
    cli = MigrationCLI(db, 'migrations')
    
    if args.command == 'status':
        cli.status()
    elif args.command == 'up':
        cli.up(args.steps)
    elif args.command == 'down':
        cli.down(args.steps)
```

# PyDBConnect Documentation (Part 9)

## Advanced Query Optimization, Monitoring, and Debugging

### 1. Query Performance Analysis

#### Query Profiler
```python
from time import time
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json
import threading

@dataclass
class QueryProfile:
    query: str
    params: tuple
    execution_time: float
    rows_affected: int
    timestamp: datetime
    trace_id: str
    execution_plan: Dict[str, Any] = None

class QueryProfiler:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._profiles: List[QueryProfile] = []
        self._local = threading.local()
        self._setup_profiling_table()

    def _setup_profiling_table(self):
        """Create table for storing query profiles."""
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS query_profiles (
                id SERIAL PRIMARY KEY,
                query TEXT NOT NULL,
                params JSONB,
                execution_time FLOAT NOT NULL,
                rows_affected INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                trace_id VARCHAR(50),
                execution_plan JSONB
            )
        """)

    def profile_query(self, query: str, params: tuple = None) -> QueryProfile:
        """Profile a single query execution."""
        start_time = time()
        result = None
        rows_affected = 0

        try:
            # Get execution plan if supported
            plan = self._get_execution_plan(query, params)
            
            # Execute actual query
            result = self.db.execute_sql_to_dataframe(query, params=params)
            rows_affected = len(result) if hasattr(result, '__len__') else 0

        finally:
            execution_time = time() - start_time
            
            profile = QueryProfile(
                query=query,
                params=params or tuple(),
                execution_time=execution_time,
                rows_affected=rows_affected,
                timestamp=datetime.now(),
                trace_id=getattr(self._local, 'trace_id', None),
                execution_plan=plan
            )
            
            self._store_profile(profile)
            return profile

    def _get_execution_plan(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Get query execution plan if supported by database."""
        try:
            if self.db.engine_type == TargetDatabaseEngine.POSTGRESQL:
                explain_query = f"EXPLAIN (FORMAT JSON) {query}"
                result = self.db.execute_sql_to_dataframe(explain_query, params=params)
                return json.loads(result.iloc[0][0])
            # Add support for other database engines
            return None
        except Exception:
            return None

    def _store_profile(self, profile: QueryProfile):
        """Store query profile in database."""
        self.db.insert("query_profiles", {
            "query": profile.query,
            "params": json.dumps(profile.params),
            "execution_time": profile.execution_time,
            "rows_affected": profile.rows_affected,
            "timestamp": profile.timestamp,
            "trace_id": profile.trace_id,
            "execution_plan": json.dumps(profile.execution_plan) if profile.execution_plan else None
        })

    def analyze_slow_queries(self, threshold_seconds: float = 1.0) -> pd.DataFrame:
        """Analyze slow queries exceeding threshold."""
        return self.db.execute_sql_to_dataframe("""
            WITH query_stats AS (
                SELECT 
                    query,
                    COUNT(*) as execution_count,
                    AVG(execution_time) as avg_execution_time,
                    MAX(execution_time) as max_execution_time,
                    MIN(execution_time) as min_execution_time,
                    AVG(rows_affected) as avg_rows_affected,
                    MAX(timestamp) as last_executed
                FROM query_profiles
                GROUP BY query
                HAVING AVG(execution_time) > ?
            )
            SELECT *
            FROM query_stats
            ORDER BY avg_execution_time DESC
        """, params=[threshold_seconds])

class ProfilingDatabaseConnection(DatabaseConnection):
    """Database connection with built-in profiling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profiler = QueryProfiler(self)
        self._local = threading.local()

    def set_trace_id(self, trace_id: str):
        """Set trace ID for current thread."""
        self._local.trace_id = trace_id

    def execute_sql_to_dataframe(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute query with profiling."""
        profile = self.profiler.profile_query(query, params)
        if profile.execution_time > 1.0:  # Log slow queries
            print(f"Slow query detected: {profile.execution_time:.2f} seconds")
            if profile.execution_plan:
                print(f"Execution plan: {json.dumps(profile.execution_plan, indent=2)}")
        return super().execute_sql_to_dataframe(query, params)
```

### 2. Query Optimization Recommendations

```python
class QueryOptimizer:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        
    def analyze_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Analyze query and provide optimization recommendations."""
        recommendations = []
        
        # Get execution plan
        plan = self._get_execution_plan(query, params)
        if plan:
            # Analyze plan for common issues
            if self._has_sequential_scan(plan):
                recommendations.append({
                    'type': 'INDEX_MISSING',
                    'description': 'Query is performing a sequential scan. Consider adding an index.',
                    'tables': self._get_tables_from_plan(plan)
                })
                
            if self._has_nested_loops(plan):
                recommendations.append({
                    'type': 'NESTED_LOOPS',
                    'description': 'Query is using nested loops. Consider improving join conditions.'
                })
                
        # Analyze query structure
        if self._has_wildcard_select(query):
            recommendations.append({
                'type': 'SELECT_ALL',
                'description': 'Using SELECT *. Consider selecting only needed columns.'
            })
            
        if self._has_multiple_joins(query):
            recommendations.append({
                'type': 'COMPLEX_JOINS',
                'description': 'Query has multiple joins. Verify if all joins are necessary.'
            })
            
        return {
            'query': query,
            'recommendations': recommendations,
            'execution_plan': plan
        }
    
    def suggest_indexes(self, query: str) -> List[str]:
        """Suggest indexes for query optimization."""
        tables = self._extract_tables(query)
        suggestions = []
        
        for table in tables:
            columns = self._extract_where_columns(query, table)
            join_columns = self._extract_join_columns(query, table)
            
            # Suggest single-column indexes
            for column in columns:
                suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column});")
            
            # Suggest composite indexes for joins
            if join_columns:
                joined_cols = '_'.join(join_columns)
                suggestions.append(f"CREATE INDEX idx_{table}_joins ON {table}({joined_cols});")
                
        return suggestions

    def generate_optimization_report(self) -> str:
        """Generate comprehensive optimization report."""
        report = []
        report.append("Database Optimization Report")
        report.append("==========================")
        
        # Table statistics
        table_stats = self._get_table_statistics()
        report.append("\nTable Statistics:")
        for stat in table_stats:
            report.append(f"- {stat['table_name']}: {stat['row_count']} rows, "
                        f"{stat['size']} disk space")
            
        # Index usage
        index_stats = self._get_index_usage_statistics()
        report.append("\nIndex Usage:")
        for stat in index_stats:
            report.append(f"- {stat['index_name']}: {stat['usage_count']} uses, "
                        f"last used: {stat['last_used']}")
            
        # Slow queries
        slow_queries = self._get_slow_queries()
        report.append("\nSlow Queries:")
        for query in slow_queries:
            report.append(f"- {query['query']} ({query['avg_time']} sec avg)")
            
        return "\n".join(report)
```

### 3. Real-time Monitoring

```python
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import json

@dataclass
class DatabaseMetrics:
    connection_count: int
    active_queries: int
    idle_queries: int
    cache_hit_ratio: float
    transaction_rate: float
    rollback_rate: float
    timestamp: datetime = datetime.now()

class DatabaseMonitor:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.metrics_history: List[DatabaseMetrics] = []
        self._setup_monitoring()

    def _setup_monitoring(self):
        """Setup monitoring tables and functions."""
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS database_metrics (
                id SERIAL PRIMARY KEY,
                connection_count INTEGER,
                active_queries INTEGER,
                idle_queries INTEGER,
                cache_hit_ratio FLOAT,
                transaction_rate FLOAT,
                rollback_rate FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    async def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring."""
        while True:
            try:
                metrics = self.collect_metrics()
                self._store_metrics(metrics)
                self._analyze_metrics(metrics)
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(5)

    def collect_metrics(self) -> DatabaseMetrics:
        """Collect current database metrics."""
        if self.db.engine_type == TargetDatabaseEngine.POSTGRESQL:
            return self._collect_postgres_metrics()
        elif self.db.engine_type == TargetDatabaseEngine.MYSQL:
            return self._collect_mysql_metrics()
        # Add support for other databases
        raise NotImplementedError(f"Monitoring not supported for {self.db.engine_type}")

    def _collect_postgres_metrics(self) -> DatabaseMetrics:
        """Collect PostgreSQL specific metrics."""
        stats = self.db.execute_sql_to_dataframe("""
            SELECT
                (SELECT count(*) FROM pg_stat_activity) as connection_count,
                (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries,
                (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_queries,
                (SELECT round(100.0 * sum(heap_blks_hit) /
                    (sum(heap_blks_hit) + sum(heap_blks_read)), 2)
                FROM pg_statio_user_tables) as cache_hit_ratio,
                (SELECT sum(xact_commit)::float / 
                    EXTRACT(epoch FROM now() - pg_postmaster_start_time())
                FROM pg_stat_database) as transaction_rate,
                (SELECT sum(xact_rollback)::float / 
                    EXTRACT(epoch FROM now() - pg_postmaster_start_time())
                FROM pg_stat_database) as rollback_rate
            FROM pg_stat_database LIMIT 1
        """).iloc[0]

        return DatabaseMetrics(
            connection_count=stats['connection_count'],
            active_queries=stats['active_queries'],
            idle_queries=stats['idle_queries'],
            cache_hit_ratio=stats['cache_hit_ratio'],
            transaction_rate=stats['transaction_rate'],
            rollback_rate=stats['rollback_rate']
        )

    def _store_metrics(self, metrics: DatabaseMetrics):
        """Store metrics in database."""
        self.db.insert("database_metrics", {
            "connection_count": metrics.connection_count,
            "active_queries": metrics.active_queries,
            "idle_queries": metrics.idle_queries,
            "cache_hit_ratio": metrics.cache_hit_ratio,
            "transaction_rate": metrics.transaction_rate,
            "rollback_rate": metrics.rollback_rate,
            "timestamp": metrics.timestamp
        })

    def _analyze_metrics(self, metrics: DatabaseMetrics):
        """Analyze metrics and generate alerts if needed."""
        alerts = []
        
        # Check connection count
        if metrics.connection_count > 100:  # Example threshold
            alerts.append({
                "level": "WARNING",
                "message": f"High connection count: {metrics.connection_count}"
            })
            
        # Check cache hit ratio
        if metrics.cache_hit_ratio < 90:  # Example threshold
            alerts.append({
                "level": "WARNING",
                "message": f"Low cache hit ratio: {metrics.cache_hit_ratio}%"
            })
            
        # Check rollback rate
        if metrics.rollback_rate > 0.1:  # Example threshold
            alerts.append({
                "level": "ERROR",
                "message": f"High rollback rate: {metrics.rollback_rate}"
            })
            
        if alerts:
            self._send_alerts(alerts)

    def _send_alerts(self, alerts: List[Dict]):
        """Send alerts through configured channels."""
        for alert in alerts:
            print(f"ALERT [{alert['level']}]: {alert['message']}")
            # Implement actual alert sending (email, Slack, etc.)
```

## Integration Patterns with Popular Frameworks and Tools

### 1. FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Optional, List
from contextlib import asynccontextmanager
import asyncio
from pydantic import BaseModel

class DatabaseSettings(BaseModel):
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 5

class FastAPIIntegration:
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self.pool = MonitoredConnectionPool(
            min_size=settings.pool_size,
            max_size=settings.pool_size * 2,
            **settings.dict(exclude_none=True)
        )
        self._setup_monitoring()

    async def startup(self):
        """Initialize database connection pool on startup."""
        await self._initialize_pool()
        self.monitor_task = asyncio.create_task(self._monitor_connections())

    async def shutdown(self):
        """Clean up database connections on shutdown."""
        if hasattr(self, 'monitor_task'):
            self.monitor_task.cancel()
        await self.pool.cleanup()

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool."""
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

    def get_db_dependency(self):
        """Create FastAPI dependency for database connection."""
        async def _get_db():
            async with self.get_connection() as db:
                yield db
        return _get_db

# FastAPI Application Setup
app = FastAPI()
db_settings = DatabaseSettings(
    host="localhost",
    port=5432,
    database="myapp"
)
db_integration = FastAPIIntegration(db_settings)

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await db_integration.startup()

@app.on_event("shutdown")
async def shutdown():
    await db_integration.shutdown()

# Database dependency
get_db = db_integration.get_db_dependency()

# API Routes with Database Integration
class User(BaseModel):
    id: Optional[int]
    username: str
    email: str

@app.post("/users/", response_model=User)
async def create_user(user: User, db: DatabaseConnection = Depends(get_db)):
    try:
        user_id = db.insert("users", user.dict(exclude={'id'}))
        return {**user.dict(), "id": user_id}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, db: DatabaseConnection = Depends(get_db)):
    result = db.select("users", where={"id": user_id})
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**result[0])
```

### 2. Flask Integration

```python
from flask import Flask, g, request
from werkzeug.local import LocalProxy
from typing import Optional

class FlaskDatabaseIntegration:
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize Flask application with database integration."""
        app.config.setdefault('DATABASE_HOST', 'localhost')
        app.config.setdefault('DATABASE_PORT', 5432)
        app.config.setdefault('DATABASE_NAME', 'myapp')
        
        app.teardown_appcontext(self.teardown)
        
    def connect(self) -> DatabaseConnection:
        """Create new database connection."""
        if not hasattr(g, 'db'):
            g.db = DatabaseConnection(
                TargetDatabaseEngine.POSTGRESQL,
                TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
            ).finalization_of_connection_parameters(
                host=self.app.config['DATABASE_HOST'],
                port=self.app.config['DATABASE_PORT'],
                database=self.app.config['DATABASE_NAME']
            ).connect_to_database()
        return g.db

    def teardown(self, exception):
        """Clean up database connection."""
        db = g.pop('db', None)
        if db is not None:
            db.close()

def get_db() -> DatabaseConnection:
    """Get database connection for current context."""
    if 'db' not in g:
        g.db = current_app.extensions['database'].connect()
    return g.db

# Create database proxy
db = LocalProxy(get_db)

# Flask Application Setup
app = Flask(__name__)
database = FlaskDatabaseIntegration(app)

# Route Examples
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user_id = db.insert("users", data)
        return {"id": user_id, **data}, 201
    except DatabaseError as e:
        return {"error": str(e)}, 500

@app.route('/users/<int:user_id>')
def get_user(user_id):
    try:
        user = db.select("users", where={"id": user_id})
        if not user:
            return {"error": "User not found"}, 404
        return user[0]
    except DatabaseError as e:
        return {"error": str(e)}, 500
```

### 3. Django Integration

```python
from django.db import connections
from django.conf import settings
from typing import Any, Dict

class DjangoDatabaseWrapper:
    """Custom database wrapper for Django integration."""
    
    def __init__(self, settings_dict: Dict[str, Any]):
        self.settings_dict = settings_dict
        self.connection = None
        self._init_connection()

    def _init_connection(self):
        """Initialize database connection with settings."""
        self.connection = DatabaseConnection(
            TargetDatabaseEngine[self.settings_dict['ENGINE'].upper()],
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        ).finalization_of_connection_parameters(
            host=self.settings_dict['HOST'],
            port=self.settings_dict['PORT'],
            database=self.settings_dict['NAME']
        )

        if self.settings_dict.get('USER'):
            self.connection._credentials = {
                'username': self.settings_dict['USER'],
                'password': self.settings_dict.get('PASSWORD', ''),
                'is_default': False
            }

        self.connection.connect_to_database()

    def cursor(self):
        """Get database cursor."""
        return self.connection._cursor()

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

# Django database settings
DATABASES = {
    'default': {
        'ENGINE': 'pydbconnect.django',
        'NAME': 'myapp',
        'USER': 'dbuser',
        'PASSWORD': 'dbpass',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# Django model example
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    @classmethod
    def custom_query(cls):
        """Example of custom query using PyDBConnect."""
        with connections['default'].cursor() as cursor:
            return cursor.execute_sql_to_dataframe("""
                SELECT username, email, created_at
                FROM users
                ORDER BY created_at DESC
            """)
```

### 4. SQLAlchemy Integration

```python
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.sql import ClauseElement
from typing import Any, Dict, Optional

class SQLAlchemyIntegration:
    """SQLAlchemy integration for PyDBConnect."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._connection = None

    def execute(self, statement: ClauseElement, parameters: Optional[Dict[str, Any]] = None):
        """Execute SQLAlchemy statement."""
        query, params = self._compile(statement, parameters)
        return self.db.execute_sql_to_dataframe(query, params=params)

    def _compile(self, statement: ClauseElement, parameters: Optional[Dict[str, Any]] = None):
        """Compile SQLAlchemy statement to SQL."""
        if parameters is None:
            parameters = {}

        if not isinstance(statement, str):
            # Compile the statement
            compiled = statement.compile(
                dialect=self.dialect,
                compile_kwargs={"literal_binds": True}
            )
            query = str(compiled)
            parameters = compiled.params
        else:
            query = statement

        return query, parameters

# Usage with SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.sql import select

# Create engine and metadata
engine = create_engine('postgresql://user:pass@localhost/myapp')
metadata = MetaData()

# Define table
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String),
    Column('email', String)
)

# Create integration
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    database="myapp"
).connect_to_database()

integration = SQLAlchemyIntegration(db)

# Execute queries
query = select([users]).where(users.c.username == 'john')
results = integration.execute(query)
```

# PyDBConnect Documentation (Part 11)

## Advanced Use Cases and Enterprise Patterns

### 1. Enterprise Database Management

#### Database Cluster Management
```python
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import asyncio

class NodeRole(Enum):
    PRIMARY = "primary"
    REPLICA = "replica"
    STANDBY = "standby"

@dataclass
class DatabaseNode:
    host: str
    port: int
    role: NodeRole
    status: str
    lag: Optional[float] = None
    last_checked: Optional[datetime] = None

class DatabaseClusterManager:
    def __init__(self, nodes: List[Dict[str, Any]]):
        self.nodes = {
            node['host']: DatabaseNode(**node)
            for node in nodes
        }
        self.connection_pools: Dict[str, MonitoredConnectionPool] = {}
        self._initialize_pools()

    def _initialize_pools(self):
        """Initialize connection pools for all nodes."""
        for host, node in self.nodes.items():
            self.connection_pools[host] = MonitoredConnectionPool(
                min_size=5,
                max_size=20,
                host=node.host,
                port=node.port
            )

    async def monitor_cluster(self, interval: int = 30):
        """Continuously monitor cluster health."""
        while True:
            try:
                await self._check_nodes()
                await self._manage_replication()
                await asyncio.sleep(interval)
            except Exception as e:
                logging.error(f"Cluster monitoring error: {e}")
                await asyncio.sleep(5)

    async def _check_nodes(self):
        """Check health of all nodes."""
        for host, node in self.nodes.items():
            try:
                pool = self.connection_pools[host]
                with pool.get_connection() as conn:
                    # Check node status
                    if node.role == NodeRole.REPLICA:
                        lag = self._check_replication_lag(conn)
                        node.lag = lag
                    node.status = "healthy"
                    node.last_checked = datetime.now()
            except Exception as e:
                node.status = "unhealthy"
                logging.error(f"Node {host} health check failed: {e}")

    def _check_replication_lag(self, conn: DatabaseConnection) -> float:
        """Check replication lag for replica nodes."""
        if conn.engine_type == TargetDatabaseEngine.POSTGRESQL:
            result = conn.execute_sql_to_dataframe("""
                SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
                AS lag
            """)
            return result.iloc[0]['lag']
        # Add support for other databases
        return None

    async def get_optimal_connection(self, read_only: bool = False) -> DatabaseConnection:
        """Get connection to optimal node based on role and health."""
        available_nodes = [
            node for node in self.nodes.values()
            if node.status == "healthy" and
            (not read_only or node.role != NodeRole.PRIMARY)
        ]

        if not available_nodes:
            raise DatabaseError("No healthy nodes available")

        # Select optimal node based on load and lag
        optimal_node = min(
            available_nodes,
            key=lambda n: (n.lag or 0) if n.role == NodeRole.REPLICA else 0
        )

        return self.connection_pools[optimal_node.host].get_connection()

class EnterpriseDatabase:
    """Enterprise database management with high availability."""
    
    def __init__(self, cluster_config: Dict[str, Any]):
        self.cluster = DatabaseClusterManager(cluster_config['nodes'])
        self.retry_policy = RetryPolicy()

    @contextmanager
    def get_connection(self, read_only: bool = False):
        """Get database connection with automatic failover."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                conn = self.cluster.get_optimal_connection(read_only)
                yield conn
                break
            except DatabaseError as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise
                logging.warning(f"Connection failed, retrying: {e}")
                time.sleep(self.retry_policy.get_delay(retry_count))

    def execute_with_failover(self, query: str, params: Optional[tuple] = None):
        """Execute query with automatic failover support."""
        with self.get_connection() as conn:
            try:
                return conn.execute_sql_to_dataframe(query, params=params)
            except DatabaseError as e:
                if self._is_recoverable_error(e):
                    # Try on another node
                    with self.get_connection() as failover_conn:
                        return failover_conn.execute_sql_to_dataframe(
                            query, params=params
                        )
                raise

    def _is_recoverable_error(self, error: Exception) -> bool:
        """Check if error is recoverable for failover."""
        recoverable_errors = {
            'connection reset',
            'connection lost',
            'timeout expired'
        }
        error_msg = str(error).lower()
        return any(msg in error_msg for msg in recoverable_errors)

# Usage Example
cluster_config = {
    'nodes': [
        {
            'host': 'primary.db.example.com',
            'port': 5432,
            'role': NodeRole.PRIMARY,
            'status': 'unknown'
        },
        {
            'host': 'replica1.db.example.com',
            'port': 5432,
            'role': NodeRole.REPLICA,
            'status': 'unknown'
        },
        {
            'host': 'replica2.db.example.com',
            'port': 5432,
            'role': NodeRole.REPLICA,
            'status': 'unknown'
        }
    ]
}

db = EnterpriseDatabase(cluster_config)

# Read from replica
with db.get_connection(read_only=True) as conn:
    result = conn.execute_sql_to_dataframe(
        "SELECT * FROM users WHERE status = ?",
        params=('active',)
    )

# Write to primary
with db.get_connection() as conn:
    with conn.transaction():
        conn.insert("users", {
            "username": "john",
            "email": "john@example.com"
        })
```

### 2. Advanced Sharding Support

```python
from typing import Optional, List, Any
import hashlib

class ShardingStrategy:
    def get_shard(self, key: Any) -> int:
        """Get shard number for given key."""
        raise NotImplementedError

class HashShardingStrategy(ShardingStrategy):
    def __init__(self, shard_count: int):
        self.shard_count = shard_count

    def get_shard(self, key: Any) -> int:
        """Get shard using consistent hashing."""
        hash_value = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        return hash_value % self.shard_count

class RangeShardingStrategy(ShardingStrategy):
    def __init__(self, ranges: List[tuple]):
        self.ranges = ranges  # List of (min, max, shard_number)

    def get_shard(self, key: Any) -> int:
        """Get shard based on range."""
        for min_val, max_val, shard in self.ranges:
            if min_val <= key <= max_val:
                return shard
        raise ValueError(f"No shard found for key: {key}")

class ShardedDatabaseConnection:
    def __init__(self, shards: List[DatabaseConnection], 
                 strategy: ShardingStrategy):
        self.shards = shards
        self.strategy = strategy

    def _get_shard(self, key: Any) -> DatabaseConnection:
        """Get appropriate shard for key."""
        shard_number = self.strategy.get_shard(key)
        return self.shards[shard_number]

    def insert(self, table: str, data: Dict[str, Any], 
              shard_key: str) -> int:
        """Insert data into appropriate shard."""
        shard = self._get_shard(data[shard_key])
        return shard.insert(table, data)

    def select(self, table: str, shard_key: Optional[Any] = None, 
              **kwargs) -> List[Dict[str, Any]]:
        """Select data from shards."""
        if shard_key is not None:
            # Query specific shard
            shard = self._get_shard(shard_key)
            return shard.select(table, **kwargs)
        else:
            # Query all shards and combine results
            results = []
            for shard in self.shards:
                results.extend(shard.select(table, **kwargs))
            return results

    def execute_on_all_shards(self, query: str, 
                            params: Optional[tuple] = None) -> List[Any]:
        """Execute query on all shards."""
        results = []
        for shard in self.shards:
            result = shard.execute_sql_to_dataframe(query, params=params)
            results.append(result)
        return results

# Usage Example
def setup_sharded_database():
    # Create connections for each shard
    shards = [
        DatabaseConnection(
            TargetDatabaseEngine.POSTGRESQL,
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        ).finalization_of_connection_parameters(
            host=f"shard{i}.db.example.com",
            database=f"myapp_shard{i}"
        ).connect_to_database()
        for i in range(3)
    ]

    # Create sharding strategy
    strategy = HashShardingStrategy(len(shards))

    # Create sharded connection
    return ShardedDatabaseConnection(shards, strategy)

# Use sharded database
sharded_db = setup_sharded_database()

# Insert data (will go to appropriate shard)
user_id = sharded_db.insert("users", {
    "id": 12345,
    "username": "john",
    "email": "john@example.com"
}, shard_key="id")

# Query specific shard
user = sharded_db.select("users", shard_key=12345, 
                        where={"id": 12345})

# Query all shards
all_users = sharded_db.select("users", 
                             where={"status": "active"})
```

## Security Patterns, Audit Logging, and Compliance Features

### 1. Enhanced Security Features

#### Secure Connection Manager
```python
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
import ssl
import logging
import jwt
from datetime import datetime, timedelta

class SecureConnectionManager:
    def __init__(self, ssl_context: Optional[ssl.SSLContext] = None,
                 encryption_key: Optional[str] = None):
        self.ssl_context = ssl_context or self._create_default_ssl_context()
        self.cipher = Fernet(encryption_key.encode() if encryption_key 
                           else Fernet.generate_key())
        self.access_tokens: Dict[str, datetime] = {}

    def _create_default_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context with modern configurations."""
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        return context

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, bytes]:
        """Encrypt sensitive connection credentials."""
        return {
            key: self.cipher.encrypt(str(value).encode())
            for key, value in credentials.items()
        }

    def decrypt_credentials(self, encrypted: Dict[str, bytes]) -> Dict[str, str]:
        """Decrypt connection credentials."""
        return {
            key: self.cipher.decrypt(value).decode()
            for key, value in encrypted.items()
        }

    def generate_access_token(self, user_id: str, 
                            permissions: List[str]) -> str:
        """Generate JWT access token for database access."""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, self.encryption_key, algorithm='HS256')
        self.access_tokens[token] = datetime.utcnow()
        return token

    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT access token and return payload."""
        try:
            payload = jwt.decode(token, self.encryption_key, 
                               algorithms=['HS256'])
            if token in self.access_tokens:
                return payload
            raise ValueError("Token not found in active sessions")
        except jwt.ExpiredSignatureError:
            self._cleanup_expired_tokens()
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def _cleanup_expired_tokens(self):
        """Remove expired tokens from tracking."""
        now = datetime.utcnow()
        expired = [
            token for token, timestamp in self.access_tokens.items()
            if (now - timestamp).total_seconds() > 3600
        ]
        for token in expired:
            del self.access_tokens[token]

class SecureDatabaseConnection(DatabaseConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.security_manager = SecureConnectionManager()
        self._access_token: Optional[str] = None

    def set_access_token(self, token: str):
        """Set access token for connection."""
        self.security_manager.validate_access_token(token)
        self._access_token = token

    def _validate_operation(self, operation: str):
        """Validate operation against token permissions."""
        if not self._access_token:
            raise SecurityError("No access token provided")
        
        payload = self.security_manager.validate_access_token(
            self._access_token)
        if operation not in payload['permissions']:
            raise SecurityError(f"Operation {operation} not permitted")
```

### 2. Comprehensive Audit Logging

```python
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

class AuditLogEntry:
    def __init__(self, 
                 operation: str,
                 user_id: str,
                 target_table: str,
                 query: str,
                 parameters: Optional[Dict] = None,
                 affected_rows: int = 0,
                 status: str = "success",
                 error_message: Optional[str] = None):
        self.timestamp = datetime.utcnow()
        self.operation = operation
        self.user_id = user_id
        self.target_table = target_table
        self.query = query
        self.parameters = parameters
        self.affected_rows = affected_rows
        self.status = status
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log entry to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'operation': self.operation,
            'user_id': self.user_id,
            'target_table': self.target_table,
            'query': self.query,
            'parameters': json.dumps(self.parameters),
            'affected_rows': self.affected_rows,
            'status': self.status,
            'error_message': self.error_message
        }

class AuditLogger:
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._setup_audit_table()

    def _setup_audit_table(self):
        """Create audit log table if it doesn't exist."""
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                operation VARCHAR(50) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                target_table VARCHAR(100) NOT NULL,
                query TEXT NOT NULL,
                parameters TEXT,
                affected_rows INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def log_operation(self, entry: AuditLogEntry):
        """Log database operation to audit log."""
        self.db.insert("audit_log", entry.to_dict())

    def get_user_operations(self, user_id: str, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[Dict]:
        """Get audit log entries for specific user."""
        query = "SELECT * FROM audit_log WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp DESC"
        return self.db.execute_sql_to_dataframe(query, 
                                              params=params).to_dict('records')

    def get_table_operations(self, table_name: str, 
                           operation_type: Optional[str] = None) -> List[Dict]:
        """Get audit log entries for specific table."""
        query = "SELECT * FROM audit_log WHERE target_table = ?"
        params = [table_name]

        if operation_type:
            query += " AND operation = ?"
            params.append(operation_type)

        query += " ORDER BY timestamp DESC"
        return self.db.execute_sql_to_dataframe(query, 
                                              params=params).to_dict('records')

class AuditedDatabaseConnection(DatabaseConnection):
    """Database connection with built-in audit logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audit_logger = AuditLogger(self)
        self._current_user_id: Optional[str] = None

    def set_user_context(self, user_id: str):
        """Set current user context for audit logging."""
        self._current_user_id = user_id

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert with audit logging."""
        try:
            result = super().insert(table, data)
            self.audit_logger.log_operation(AuditLogEntry(
                operation="INSERT",
                user_id=self._current_user_id,
                target_table=table,
                query="INSERT INTO " + table,
                parameters=data,
                affected_rows=1
            ))
            return result
        except Exception as e:
            self.audit_logger.log_operation(AuditLogEntry(
                operation="INSERT",
                user_id=self._current_user_id,
                target_table=table,
                query="INSERT INTO " + table,
                parameters=data,
                status="error",
                error_message=str(e)
            ))
            raise

    def update(self, table: str, data: Dict[str, Any], 
               where: Dict[str, Any]) -> int:
        """Update with audit logging."""
        try:
            affected = super().update(table, data, where)
            self.audit_logger.log_operation(AuditLogEntry(
                operation="UPDATE",
                user_id=self._current_user_id,
                target_table=table,
                query="UPDATE " + table,
                parameters={'data': data, 'where': where},
                affected_rows=affected
            ))
            return affected
        except Exception as e:
            self.audit_logger.log_operation(AuditLogEntry(
                operation="UPDATE",
                user_id=self._current_user_id,
                target_table=table,
                query="UPDATE " + table,
                parameters={'data': data, 'where': where},
                status="error",
                error_message=str(e)
            ))
            raise

# Usage Example
db = AuditedDatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)
db.set_user_context("admin_user")

# Operations will be automatically logged
with db.transaction():
    user_id = db.insert("users", {
        "username": "john_doe",
        "email": "john@example.com"
    })
    
    db.update("users", 
              {"status": "active"},
              {"id": user_id})

# Query audit log
user_actions = db.audit_logger.get_user_operations("admin_user")
table_actions = db.audit_logger.get_table_operations("users", "INSERT")
```

## Compliance Features, Data Masking, and Encryption Patterns

### 1. Data Protection and Compliance

#### Data Masking Service
```python
from typing import Dict, Any, List, Pattern
import re
from enum import Enum
import hashlib
from dataclasses import dataclass

class MaskingStrategy(Enum):
    FULL = "full"          # Complete masking
    PARTIAL = "partial"    # Show partial data
    HASH = "hash"          # Hash the data
    FORMAT = "format"      # Custom format
    RANDOMIZE = "random"   # Replace with random data

@dataclass
class MaskingRule:
    field: str
    strategy: MaskingStrategy
    pattern: Optional[str] = None
    format_string: Optional[str] = None
    visible_chars: int = 4

class DataMaskingService:
    def __init__(self):
        self.rules: Dict[str, List[MaskingRule]] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default masking rules for common sensitive data."""
        self.add_rule("email", MaskingRule(
            field="email",
            strategy=MaskingStrategy.PARTIAL,
            visible_chars=3
        ))
        self.add_rule("credit_card", MaskingRule(
            field="credit_card",
            strategy=MaskingStrategy.FORMAT,
            format_string="XXXX-XXXX-XXXX-{last4}"
        ))
        self.add_rule("ssn", MaskingRule(
            field="ssn",
            strategy=MaskingStrategy.FORMAT,
            format_string="XXX-XX-{last4}"
        ))
        self.add_rule("password", MaskingRule(
            field="password",
            strategy=MaskingStrategy.HASH
        ))

    def add_rule(self, table: str, rule: MaskingRule):
        """Add masking rule for a table field."""
        if table not in self.rules:
            self.rules[table] = []
        self.rules[table].append(rule)

    def mask_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply masking rules to data."""
        if table not in self.rules:
            return data

        masked_data = data.copy()
        for rule in self.rules[table]:
            if rule.field in masked_data:
                masked_data[rule.field] = self._apply_mask(
                    masked_data[rule.field],
                    rule
                )
        return masked_data

    def _apply_mask(self, value: Any, rule: MaskingRule) -> str:
        """Apply specific masking strategy to value."""
        if value is None:
            return None

        value_str = str(value)
        
        if rule.strategy == MaskingStrategy.FULL:
            return "*" * len(value_str)
            
        elif rule.strategy == MaskingStrategy.PARTIAL:
            visible = min(rule.visible_chars, len(value_str))
            return value_str[:visible] + "*" * (len(value_str) - visible)
            
        elif rule.strategy == MaskingStrategy.HASH:
            return hashlib.sha256(value_str.encode()).hexdigest()
            
        elif rule.strategy == MaskingStrategy.FORMAT:
            if not rule.format_string:
                raise ValueError("Format string required for FORMAT strategy")
            return rule.format_string.format(
                last4=value_str[-4:] if len(value_str) >= 4 else value_str
            )
            
        elif rule.strategy == MaskingStrategy.RANDOMIZE:
            return self._generate_random_value(value_str)

        return value_str

    def _generate_random_value(self, original: str) -> str:
        """Generate random value maintaining format."""
        import random
        import string
        
        def get_char_type(c: str) -> str:
            if c.isdigit():
                return string.digits
            if c.isupper():
                return string.ascii_uppercase
            if c.islower():
                return string.ascii_lowercase
            return c

        return ''.join(
            random.choice(get_char_type(c)) if c.isalnum()
            else c
            for c in original
        )

class CompliantDatabaseConnection(DatabaseConnection):
    """Database connection with data masking and compliance features."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.masking_service = DataMaskingService()
        self._compliance_mode = True

    def toggle_compliance_mode(self, enabled: bool):
        """Toggle compliance mode for data masking."""
        self._compliance_mode = enabled

    def select(self, table: str, *args, **kwargs) -> List[Dict[str, Any]]:
        """Select with automatic data masking."""
        results = super().select(table, *args, **kwargs)
        
        if self._compliance_mode:
            return [
                self.masking_service.mask_data(table, row)
                for row in results
            ]
        return results

# Usage Example
class User:
    def __init__(self, username: str, email: str, 
                 credit_card: Optional[str] = None):
        self.username = username
        self.email = email
        self.credit_card = credit_card

# Setup compliant database connection
db = CompliantDatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)

# Add custom masking rules
db.masking_service.add_rule("users", MaskingRule(
    field="email",
    strategy=MaskingStrategy.FORMAT,
    format_string="{first3}***@{domain}",
    visible_chars=3
))

# Insert data
user_data = {
    "username": "john_doe",
    "email": "john.doe@example.com",
    "credit_card": "4111-1111-1111-1234"
}

db.insert("users", user_data)

# Query with masking
masked_users = db.select("users")
# Result: [
#     {
#         "username": "john_doe",
#         "email": "joh***@example.com",
#         "credit_card": "XXXX-XXXX-XXXX-1234"
#     }
# ]

# Temporarily disable masking for authorized access
db.toggle_compliance_mode(False)
unmasked_users = db.select("users")
db.toggle_compliance_mode(True)
```

### 2. Data Encryption Service

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Optional, Dict, Any

class EncryptionService:
    def __init__(self, key: Optional[str] = None):
        self._key = key or self._generate_key()
        self._cipher = Fernet(self._key.encode())
        self._encrypted_fields: Dict[str, List[str]] = {}

    def _generate_key(self) -> str:
        """Generate a new encryption key."""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

    def register_encrypted_fields(self, table: str, fields: List[str]):
        """Register fields that should be encrypted."""
        self._encrypted_fields[table] = fields

    def encrypt_value(self, value: Any) -> str:
        """Encrypt a single value."""
        if value is None:
            return None
        return self._cipher.encrypt(str(value).encode()).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a single value."""
        if encrypted_value is None:
            return None
        return self._cipher.decrypt(encrypted_value.encode()).decode()

    def encrypt_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt specified fields in data."""
        if table not in self._encrypted_fields:
            return data

        encrypted_data = data.copy()
        for field in self._encrypted_fields[table]:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt_value(
                    encrypted_data[field]
                )
        return encrypted_data

    def decrypt_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt specified fields in data."""
        if table not in self._encrypted_fields:
            return data

        decrypted_data = data.copy()
        for field in self._encrypted_fields[table]:
            if field in decrypted_data:
                decrypted_data[field] = self.decrypt_value(
                    decrypted_data[field]
                )
        return decrypted_data

class EncryptedDatabaseConnection(DatabaseConnection):
    """Database connection with field-level encryption."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_service = EncryptionService()

    def register_encrypted_fields(self, table: str, fields: List[str]):
        """Register fields that should be encrypted."""
        self.encryption_service.register_encrypted_fields(table, fields)

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert with automatic field encryption."""
        encrypted_data = self.encryption_service.encrypt_data(table, data)
        return super().insert(table, encrypted_data)

    def select(self, table: str, *args, **kwargs) -> List[Dict[str, Any]]:
        """Select with automatic field decryption."""
        results = super().select(table, *args, **kwargs)
        return [
            self.encryption_service.decrypt_data(table, row)
            for row in results
        ]

    def update(self, table: str, data: Dict[str, Any], 
               where: Dict[str, Any]) -> int:
        """Update with automatic field encryption."""
        encrypted_data = self.encryption_service.encrypt_data(table, data)
        return super().update(table, encrypted_data, where)

# Usage Example
# Setup encrypted database connection
db = EncryptedDatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)

# Register fields for encryption
db.register_encrypted_fields("users", ["ssn", "tax_id"])
db.register_encrypted_fields("payments", ["account_number"])

# Insert sensitive data
user_data = {
    "name": "John Doe",
    "ssn": "123-45-6789",
    "tax_id": "AB-12345"
}

# Data is automatically encrypted before storage
user_id = db.insert("users", user_data)

# Data is automatically decrypted when retrieved
user = db.select("users", where={"id": user_id})[0]
# Result: {
#     "name": "John Doe",
#     "ssn": "123-45-6789",
#     "tax_id": "AB-12345"
# }
```

## Data Validation, Schema Enforcement, and Data Quality Patterns

### 1. Advanced Data Validation Framework

```python
from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime
import re
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    STRICT = "strict"      # Fail on any violation
    WARN = "warn"         # Log warnings but continue
    TRANSFORM = "transform" # Attempt to fix issues

class ValidationError(Exception):
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")

@dataclass
class FieldValidator:
    name: str
    field_type: Type
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    custom_validator: Optional[callable] = None

class DataValidator:
    """Advanced data validation framework."""
    
    def __init__(self, level: ValidationLevel = ValidationLevel.STRICT):
        self.level = level
        self.validators: Dict[str, Dict[str, FieldValidator]] = {}
        self.transformers: Dict[str, Dict[str, callable]] = {}
        self._setup_default_transformers()

    def _setup_default_transformers(self):
        """Setup default data transformation functions."""
        self.default_transformers = {
            str: str.strip,
            int: lambda x: int(float(x)) if isinstance(x, str) else int(x),
            float: float,
            datetime: lambda x: (
                datetime.fromisoformat(x) 
                if isinstance(x, str) else x
            ),
            bool: lambda x: str(x).lower() in ('true', '1', 'yes', 'y')
        }

    def register_table_schema(self, table: str, 
                            validators: List[FieldValidator]):
        """Register validation schema for a table."""
        self.validators[table] = {v.name: v for v in validators}

    def register_transformer(self, table: str, field: str, 
                           transformer: callable):
        """Register custom transformation function."""
        if table not in self.transformers:
            self.transformers[table] = {}
        self.transformers[table][field] = transformer

    def validate(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against registered schema."""
        if table not in self.validators:
            return data

        validated_data = {}
        errors = []

        for field, validator in self.validators[table].items():
            value = data.get(field)

            try:
                # Check required fields
                if validator.required and value is None:
                    raise ValidationError(field, "Field is required")

                if value is not None:
                    # Transform data if needed
                    if self.level == ValidationLevel.TRANSFORM:
                        value = self._transform_value(table, field, value, 
                                                   validator.field_type)

                    # Type validation
                    if not isinstance(value, validator.field_type):
                        raise ValidationError(
                            field, 
                            f"Expected type {validator.field_type.__name__}"
                        )

                    # Length validation
                    if validator.min_length and len(str(value)) < validator.min_length:
                        raise ValidationError(
                            field,
                            f"Minimum length is {validator.min_length}"
                        )

                    if validator.max_length and len(str(value)) > validator.max_length:
                        raise ValidationError(
                            field,
                            f"Maximum length is {validator.max_length}"
                        )

                    # Pattern validation
                    if validator.pattern and isinstance(value, str):
                        if not re.match(validator.pattern, value):
                            raise ValidationError(field, "Invalid format")

                    # Range validation
                    if validator.min_value is not None and value < validator.min_value:
                        raise ValidationError(
                            field,
                            f"Minimum value is {validator.min_value}"
                        )

                    if validator.max_value is not None and value > validator.max_value:
                        raise ValidationError(
                            field,
                            f"Maximum value is {validator.max_value}"
                        )

                    # Choices validation
                    if validator.choices and value not in validator.choices:
                        raise ValidationError(
                            field,
                            f"Value must be one of {validator.choices}"
                        )

                    # Custom validation
                    if validator.custom_validator:
                        validator.custom_validator(value)

                validated_data[field] = value

            except ValidationError as e:
                if self.level == ValidationLevel.STRICT:
                    raise
                errors.append(e)

        if errors and self.level == ValidationLevel.WARN:
            for error in errors:
                logging.warning(f"Validation warning: {error}")

        return validated_data

    def _transform_value(self, table: str, field: str, 
                        value: Any, target_type: Type) -> Any:
        """Transform value to expected type."""
        # Check for custom transformer
        if (table in self.transformers and 
            field in self.transformers[table]):
            return self.transformers[table][field](value)

        # Use default transformer
        if target_type in self.default_transformers:
            try:
                return self.default_transformers[target_type](value)
            except (ValueError, TypeError):
                if self.level == ValidationLevel.STRICT:
                    raise ValidationError(
                        field,
                        f"Could not transform to {target_type.__name__}"
                    )
        return value

class ValidatedDatabaseConnection(DatabaseConnection):
    """Database connection with data validation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = DataValidator()

    def register_schema(self, table: str, schema: List[FieldValidator]):
        """Register validation schema for a table."""
        self.validator.register_table_schema(table, schema)

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert with data validation."""
        validated_data = self.validator.validate(table, data)
        return super().insert(table, validated_data)

    def update(self, table: str, data: Dict[str, Any], 
               where: Dict[str, Any]) -> int:
        """Update with data validation."""
        validated_data = self.validator.validate(table, data)
        return super().update(table, validated_data, where)

# Usage Example
def validate_age(value: int):
    if value < 0 or value > 150:
        raise ValidationError("age", "Age must be between 0 and 150")

# Setup validated database connection
db = ValidatedDatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)

# Register schema for users table
db.register_schema("users", [
    FieldValidator(
        name="username",
        field_type=str,
        required=True,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$'
    ),
    FieldValidator(
        name="email",
        field_type=str,
        required=True,
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    ),
    FieldValidator(
        name="age",
        field_type=int,
        required=True,
        custom_validator=validate_age
    ),
    FieldValidator(
        name="status",
        field_type=str,
        required=True,
        choices=['active', 'inactive', 'pending']
    )
])

# Data will be validated before insertion
try:
    user_id = db.insert("users", {
        "username": "john_doe",
        "email": "john@example.com",
        "age": 30,
        "status": "active"
    })
except ValidationError as e:
    print(f"Validation failed: {e}")

# Invalid data will raise ValidationError
try:
    db.insert("users", {
        "username": "john@doe",  # Invalid username pattern
        "email": "invalid-email",  # Invalid email format
        "age": 200,  # Age out of range
        "status": "unknown"  # Invalid status choice
    })
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 2. Schema Evolution and Migration Tracking

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class SchemaChange:
    table: str
    field: str
    change_type: str  # 'add', 'remove', 'modify'
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class SchemaTracker:
    """Track and manage schema changes over time."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self._setup_tracking_table()

    def _setup_tracking_table(self):
        """Setup schema tracking table."""
        self.db.execute_sql_to_dataframe("""
            CREATE TABLE IF NOT EXISTS schema_changes (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(100) NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                change_type VARCHAR(20) NOT NULL,
                old_value JSONB,
                new_value JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def track_change(self, change: SchemaChange):
        """Record a schema change."""
        self.db.insert("schema_changes", {
            "table_name": change.table,
            "field_name": change.field,
            "change_type": change.change_type,
            "old_value": json.dumps(change.old_value) if change.old_value else None,
            "new_value": json.dumps(change.new_value) if change.new_value else None,
            "timestamp": change.timestamp
        })

    def get_schema_history(self, table: Optional[str] = None) -> List[Dict]:
        """Get schema change history."""
        query = "SELECT * FROM schema_changes"
        params = []

        if table:
            query += " WHERE table_name = ?"
            params.append(table)

        query += " ORDER BY timestamp DESC"
        return self.db.execute_sql_to_dataframe(
            query, params=params
        ).to_dict('records')

# Usage Example
# Track schema changes when modifying validation rules
db.schema_tracker = SchemaTracker(db)

# Add new field validator
new_validator = FieldValidator(
    name="phone",
    field_type=str,
    required=False,
    pattern=r'^\+?1?\d{9,15}$'
)

old_validators = db.validator.validators.get("users", {})
db.register_schema("users", [
    *old_validators.values(),
    new_validator
])

# Track the change
db.schema_tracker.track_change(SchemaChange(
    table="users",
    field="phone",
    change_type="add",
    new_value={
        "type": "string",
        "required": False,
        "pattern": r'^\+?1?\d{9,15}$'
    }
))
```

## Advanced Querying Patterns & Optimization

### 1. Advanced Query Builder

```python
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

class JoinType(Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL JOIN"

class OrderDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"

@dataclass
class JoinClause:
    table: str
    type: JoinType
    on: Dict[str, str]  # {"left_col": "right_col"}

class QueryBuilder:
    """Advanced SQL query builder with optimization."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.reset()

    def reset(self):
        """Reset query builder state."""
        self._select_columns: List[str] = []
        self._from_table: str = ""
        self._joins: List[JoinClause] = []
        self._where_conditions: List[str] = []
        self._where_params: List[Any] = []
        self._group_by: List[str] = []
        self._having_conditions: List[str] = []
        self._having_params: List[Any] = []
        self._order_by: List[tuple] = []  # (column, direction)
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        return self

    def select(self, *columns: str) -> 'QueryBuilder':
        """Add columns to SELECT clause."""
        self._select_columns.extend(columns)
        return self

    def from_table(self, table: str) -> 'QueryBuilder':
        """Set FROM table."""
        self._from_table = table
        return self

    def join(self, table: str, on: Dict[str, str], 
             join_type: JoinType = JoinType.INNER) -> 'QueryBuilder':
        """Add JOIN clause."""
        self._joins.append(JoinClause(table, join_type, on))
        return self

    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """Add WHERE condition."""
        self._where_conditions.append(condition)
        self._where_params.extend(params)
        return self

    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """Add WHERE IN clause."""
        placeholders = ','.join(['?'] * len(values))
        self._where_conditions.append(f"{column} IN ({placeholders})")
        self._where_params.extend(values)
        return self

    def group_by(self, *columns: str) -> 'QueryBuilder':
        """Add GROUP BY clause."""
        self._group_by.extend(columns)
        return self

    def having(self, condition: str, *params: Any) -> 'QueryBuilder':
        """Add HAVING condition."""
        self._having_conditions.append(condition)
        self._having_params.extend(params)
        return self

    def order_by(self, column: str, 
                direction: OrderDirection = OrderDirection.ASC) -> 'QueryBuilder':
        """Add ORDER BY clause."""
        self._order_by.append((column, direction))
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self._offset = offset
        return self

    def build(self) -> tuple:
        """Build SQL query and parameters."""
        parts = ["SELECT"]
        
        # Select columns
        if self._select_columns:
            parts.append(", ".join(self._select_columns))
        else:
            parts.append("*")

        # From clause
        parts.append(f"FROM {self._from_table}")

        # Joins
        for join in self._joins:
            conditions = " AND ".join(
                f"{k} = {v}" for k, v in join.on.items()
            )
            parts.append(f"{join.type.value} {join.table} ON {conditions}")

        # Where clause
        if self._where_conditions:
            parts.append("WHERE " + " AND ".join(self._where_conditions))

        # Group by
        if self._group_by:
            parts.append("GROUP BY " + ", ".join(self._group_by))

        # Having
        if self._having_conditions:
            parts.append("HAVING " + " AND ".join(self._having_conditions))

        # Order by
        if self._order_by:
            order_clauses = [
                f"{col} {direction.value}"
                for col, direction in self._order_by
            ]
            parts.append("ORDER BY " + ", ".join(order_clauses))

        # Limit and offset
        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")
        if self._offset is not None:
            parts.append(f"OFFSET {self._offset}")

        query = " ".join(parts)
        params = self._where_params + self._having_params
        return query, params

    def execute(self) -> pd.DataFrame:
        """Execute the built query."""
        query, params = self.build()
        return self.db.execute_sql_to_dataframe(query, params=params)

class OptimizedQueryBuilder(QueryBuilder):
    """Query builder with additional optimization features."""

    def __init__(self, db: DatabaseConnection):
        super().__init__(db)
        self.explain_mode = False
        self._cache = QueryCache(db)

    def with_explain(self) -> 'OptimizedQueryBuilder':
        """Enable execution plan analysis."""
        self.explain_mode = True
        return self

    def execute(self) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Execute query with optional optimization."""
        query, params = self.build()
        
        # Check cache first
        if cached_result := self._cache.get(query, params):
            return cached_result

        if self.explain_mode:
            return self._execute_with_explain(query, params)
        
        result = self.db.execute_sql_to_dataframe(query, params=params)
        self._cache.set(query, params, result)
        return result

    def _execute_with_explain(self, query: str, 
                            params: tuple) -> Dict[str, Any]:
        """Execute query with EXPLAIN analysis."""
        explain_query = f"EXPLAIN (FORMAT JSON) {query}"
        execution_plan = self.db.execute_sql_to_dataframe(
            explain_query, params=params
        )

        actual_result = self.db.execute_sql_to_dataframe(
            query, params=params
        )

        return {
            'data': actual_result,
            'execution_plan': execution_plan,
            'query': query,
            'params': params
        }

# Usage Example
# Basic usage
query = (QueryBuilder(db)
    .select("users.name", "orders.total")
    .from_table("users")
    .join("orders", {"users.id": "orders.user_id"}, JoinType.LEFT)
    .where("orders.status = ?", "completed")
    .where("orders.total > ?", 100)
    .group_by("users.name")
    .having("COUNT(*) > ?", 5)
    .order_by("orders.total", OrderDirection.DESC)
    .limit(10)
)

results = query.execute()

# Optimized usage with execution plan analysis
optimized_query = (OptimizedQueryBuilder(db)
    .select("users.name", "SUM(orders.total) as total_orders")
    .from_table("users")
    .join("orders", {"users.id": "orders.user_id"}, JoinType.INNER)
    .where("orders.created_at > ?", "2024-01-01")
    .group_by("users.name")
    .having("total_orders > ?", 1000)
    .with_explain()
)

results = optimized_query.execute()
print(f"Execution Plan: {results['execution_plan']}")
```

### 2. Query Performance Optimization

```python
from typing import List, Set, Dict, Any
import time
from dataclasses import dataclass

@dataclass
class QueryMetrics:
    query: str
    params: tuple
    execution_time: float
    rows_returned: int
    cached: bool = False

class QueryOptimizer:
    """Query performance optimization and monitoring."""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.metrics: List[QueryMetrics] = []
        self.slow_query_threshold = 1.0  # seconds
        self._table_statistics = {}
        self._update_table_statistics()

    def _update_table_statistics(self):
        """Update table statistics for optimization."""
        if self.db.engine_type == TargetDatabaseEngine.POSTGRESQL:
            stats = self.db.execute_sql_to_dataframe("""
                SELECT
                    schemaname,
                    tablename,
                    n_live_tup as row_count,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_analyze
                FROM pg_stat_user_tables
            """)
            
            for _, row in stats.iterrows():
                self._table_statistics[row['tablename']] = {
                    'row_count': row['row_count'],
                    'dead_rows': row['dead_rows'],
                    'last_vacuum': row['last_vacuum'],
                    'last_analyze': row['last_analyze']
                }

    def analyze_query(self, query: str, 
                     params: tuple = None) -> Dict[str, Any]:
        """Analyze query for potential optimizations."""
        start_time = time.time()
        explain_result = self.db.execute_sql_to_dataframe(
            f"EXPLAIN (FORMAT JSON) {query}",
            params=params
        )
        execution_time = time.time() - start_time

        plan = explain_result.iloc[0][0]
        recommendations = []

        # Analyze execution plan
        if 'Seq Scan' in str(plan):
            recommendations.append({
                'type': 'INDEX',
                'message': 'Consider adding an index to avoid sequential scan'
            })

        if execution_time > self.slow_query_threshold:
            recommendations.append({
                'type': 'PERFORMANCE',
                'message': f'Query execution time ({execution_time:.2f}s) '
                          f'exceeds threshold ({self.slow_query_threshold}s)'
            })

        return {
            'execution_plan': plan,
            'execution_time': execution_time,
            'recommendations': recommendations
        }

    def suggest_indexes(self, query: str) -> List[str]:
        """Suggest indexes for query optimization."""
        analysis = self.analyze_query(query)
        suggestions = []

        plan = analysis['execution_plan']
        tables_columns = self._extract_tables_columns(query)

        for table, columns in tables_columns.items():
            # Check table statistics
            stats = self._table_statistics.get(table, {})
            row_count = stats.get('row_count', 0)

            # Suggest indexes for large tables
            if row_count > 10000:
                for col in columns:
                    if self._should_create_index(table, col, row_count):
                        suggestions.append(
                            f"CREATE INDEX idx_{table}_{col} ON {table}({col})"
                        )

        return suggestions

    def _should_create_index(self, table: str, column: str, 
                           row_count: int) -> bool:
        """Determine if an index would be beneficial."""
        # Check existing indexes
        existing_indexes = self.db.execute_sql_to_dataframe(f"""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = '{table}'
        """)

        # Check if column is already indexed
        for _, idx in existing_indexes.iterrows():
            if column in idx['indexdef']:
                return False

        # Analyze column cardinality
        distinct_count = self.db.execute_sql_to_dataframe(f"""
            SELECT COUNT(DISTINCT {column}) as distinct_count
            FROM {table}
        """).iloc[0]['distinct_count']

        # Suggest index if cardinality is high enough
        return distinct_count / row_count > 0.1

    def optimize_query(self, query: str, 
                      params: tuple = None) -> Dict[str, Any]:
        """Optimize query and provide execution statistics."""
        # Analyze original query
        original_analysis = self.analyze_query(query, params)
        
        # Try optimization techniques
        optimized_query = self._apply_optimizations(query)
        optimized_analysis = self.analyze_query(optimized_query, params)

        return {
            'original_query': query,
            'optimized_query': optimized_query,
            'performance_improvement': (
                original_analysis['execution_time'] -
                optimized_analysis['execution_time']
            ),
            'original_plan': original_analysis['execution_plan'],
            'optimized_plan': optimized_analysis['execution_plan']
        }

    def _apply_optimizations(self, query: str) -> str:
        """Apply various optimization techniques to the query."""
        optimized = query

        # Remove unnecessary columns
        if 'SELECT *' in optimized:
            tables_columns = self._extract_tables_columns(query)
            needed_columns = self._analyze_needed_columns(query)
            optimized = self._replace_star_with_columns(
                optimized, 
                needed_columns
            )

        # Optimize JOIN order
        if 'JOIN' in optimized:
            optimized = self._optimize_join_order(optimized)

        # Add LIMIT if missing
        if 'LIMIT' not in optimized.upper():
            optimized += " LIMIT 1000"

        return optimized

# Usage Example
optimizer = QueryOptimizer(db)

# Analyze and optimize a complex query
query = """
SELECT users.*, orders.total, products.name
FROM users
JOIN orders ON users.id = orders.user_id
JOIN products ON orders.product_id = products.id
WHERE orders.status = 'completed'
  AND orders.created_at > '2024-01-01'
GROUP BY users.id, orders.total, products.name
HAVING COUNT(*) > 5
"""

# Get optimization suggestions
analysis = optimizer.analyze_query(query)
print("Recommendations:", analysis['recommendations'])

# Get index suggestions
index_suggestions = optimizer.suggest_indexes(query)
print("Suggested indexes:", index_suggestions)

# Optimize query
optimization_result = optimizer.optimize_query(query)
print(f"Performance improvement: {optimization_result['performance_improvement']:.2f}s")
```

## Production Deployment & Best Practices

### 1. Production Ready Connection Manager

```python
from typing import Dict, Optional, List
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime, timedelta

class ProductionConnectionManager:
    """Production-grade database connection manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pools: Dict[str, MonitoredConnectionPool] = {}
        self.health_check_interval = config.get('health_check_interval', 60)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.monitoring_enabled = config.get('monitoring_enabled', True)
        self._setup_logging()
        self._initialize_pools()
        self._start_health_checks()

    def _setup_logging(self):
        """Configure production logging."""
        self.logger = logging.getLogger('PyDBConnect')
        self.logger.setLevel(logging.INFO)
        
        # File handler for persistent logging
        fh = logging.FileHandler('database.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(fh)
        
        # Metrics handler for monitoring
        if self.monitoring_enabled:
            self.metrics_handler = MetricsHandler()
            self.logger.addHandler(self.metrics_handler)

    def _initialize_pools(self):
        """Initialize connection pools for different database roles."""
        for role, settings in self.config['databases'].items():
            self.pools[role] = MonitoredConnectionPool(
                min_size=settings.get('min_connections', 5),
                max_size=settings.get('max_connections', 20),
                idle_timeout=settings.get('idle_timeout', 300),
                **settings['connection_params']
            )

    def _start_health_checks(self):
        """Start background health check thread."""
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()

    def _health_check_loop(self):
        """Continuous health check loop."""
        while True:
            try:
                self._check_all_pools()
                time.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check error: {e}")

    def _check_all_pools(self):
        """Check health of all connection pools."""
        for role, pool in self.pools.items():
            stats = pool.get_stats()
            self.logger.info(f"Pool {role} stats: {stats}")
            
            # Check for warning signs
            if stats['active_connections'] / stats['max_connections'] > 0.8:
                self.logger.warning(
                    f"Pool {role} nearing capacity: "
                    f"{stats['active_connections']}/{stats['max_connections']}"
                )

            if stats['failed_connections'] > 0:
                self.logger.error(
                    f"Pool {role} has {stats['failed_connections']} "
                    "failed connections"
                )

class ProductionDatabase:
    """Production-ready database interface."""
    
    def __init__(self, manager: ProductionConnectionManager):
        self.manager = manager
        self.retrier = ExponentialRetry(
            max_retries=manager.max_retries,
            base_delay=manager.retry_delay
        )

    @contextmanager
    def get_connection(self, role: str = 'primary') -> DatabaseConnection:
        """Get database connection with automatic retry and monitoring."""
        start_time = time.time()
        try:
            conn = self.manager.pools[role].get_connection()
            try:
                yield conn
                self._record_success(role, time.time() - start_time)
            finally:
                self.manager.pools[role].return_connection(conn)
        except Exception as e:
            self._record_failure(role, e)
            raise

    def execute_with_retry(self, operation: callable, 
                         role: str = 'primary') -> Any:
        """Execute database operation with retry logic."""
        return self.retrier.execute(
            lambda: self._execute_operation(operation, role)
        )

    def _execute_operation(self, operation: callable, role: str) -> Any:
        """Execute single database operation."""
        with self.get_connection(role) as conn:
            return operation(conn)

    def _record_success(self, role: str, duration: float):
        """Record successful database operation."""
        self.manager.logger.info(
            f"Operation succeeded on {role} in {duration:.2f}s"
        )
        if self.manager.monitoring_enabled:
            self.manager.metrics_handler.record_metric(
                'database_operation_duration',
                duration,
                {'role': role, 'status': 'success'}
            )

    def _record_failure(self, role: str, error: Exception):
        """Record failed database operation."""
        self.manager.logger.error(
            f"Operation failed on {role}: {error}"
        )
        if self.manager.monitoring_enabled:
            self.manager.metrics_handler.record_metric(
                'database_operation_failures',
                1,
                {'role': role, 'error': type(error).__name__}
            )

class ExponentialRetry:
    """Exponential backoff retry mechanism."""
    
    def __init__(self, max_retries: int, base_delay: float):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute(self, operation: callable) -> Any:
        """Execute operation with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return operation()
            except Exception as e:
                last_error = e
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)
        
        raise last_error

class MetricsHandler(logging.Handler):
    """Handler for collecting and exporting metrics."""
    
    def __init__(self):
        super().__init__()
        self.metrics: Dict[str, List[Dict]] = {}

    def emit(self, record: logging.LogRecord):
        """Process log record for metrics."""
        if hasattr(record, 'metrics'):
            self._store_metric(record.metrics)

    def record_metric(self, name: str, value: float, labels: Dict[str, str]):
        """Record a metric with labels."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'labels': labels,
            'timestamp': datetime.now()
        })

    def export_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        for name, measurements in self.metrics.items():
            for m in measurements:
                labels = ','.join(
                    f'{k}="{v}"'
                    for k, v in m['labels'].items()
                )
                lines.append(
                    f'{name}{{{labels}}} {m["value"]} '
                    f'{int(m["timestamp"].timestamp() * 1000)}'
                )
        return '\n'.join(lines)

# Usage Example
config = {
    'databases': {
        'primary': {
            'connection_params': {
                'host': 'primary.db.example.com',
                'port': 5432,
                'database': 'myapp'
            },
            'min_connections': 10,
            'max_connections': 50
        },
        'replica': {
            'connection_params': {
                'host': 'replica.db.example.com',
                'port': 5432,
                'database': 'myapp'
            },
            'min_connections': 5,
            'max_connections': 20
        }
    },
    'health_check_interval': 30,
    'max_retries': 3,
    'retry_delay': 1,
    'monitoring_enabled': True
}

# Initialize production database
manager = ProductionConnectionManager(config)
db = ProductionDatabase(manager)

# Example usage with retry and monitoring
def create_user(conn: DatabaseConnection, user_data: Dict):
    return conn.insert('users', user_data)

try:
    user_id = db.execute_with_retry(
        lambda conn: create_user(conn, {
            'username': 'john_doe',
            'email': 'john@example.com'
        })
    )
except Exception as e:
    logging.error(f"Failed to create user: {e}")

# Export metrics
metrics = manager.metrics_handler.export_metrics()
print(metrics)
```

### 2. Best Practices & Anti-Patterns

```python
# Best Practices Guide

# 1. Connection Management
# ✅ DO: Use connection pooling
with db.get_connection() as conn:
    result = conn.execute_query(...)

# ❌ DON'T: Create new connections for each operation
conn = DatabaseConnection(...)  # Avoid this
result = conn.execute_query(...)
conn.close()

# 2. Transaction Management
# ✅ DO: Use transaction context managers
with db.transaction():
    db.insert(...)
    db.update(...)

# ❌ DON'T: Manage transactions manually
db.begin()  # Avoid this
try:
    db.insert(...)
    db.update(...)
    db.commit()
except:
    db.rollback()

# 3. Query Optimization
# ✅ DO: Use parameterized queries
db.select("users", where={"id": user_id})

# ❌ DON'T: Use string formatting for queries
db.execute(f"SELECT * FROM users WHERE id = {user_id}")  # NEVER do this

# 4. Error Handling
# ✅ DO: Use specific error handling
try:
    db.insert(...)
except DuplicateKeyError:
    handle_duplicate()
except DatabaseError as e:
    handle_error(e)

# ❌ DON'T: Catch all exceptions
try:
    db.insert(...)
except Exception:  # Too broad
    pass

# 5. Resource Management
# ✅ DO: Use context managers
with db.cursor() as cursor:
    cursor.execute(...)

# ❌ DON'T: Leave resources open
cursor = db.cursor()  # Resource leak risk
cursor.execute(...)

# 6. Batch Operations
# ✅ DO: Use bulk operations
db.bulk_insert("users", users_data)

# ❌ DON'T: Loop through individual inserts
for user in users_data:  # Inefficient
    db.insert("users", user)

# 7. Monitoring and Logging
# ✅ DO: Include context in logs
db.logger.error("Query failed", extra={
    "query": query,
    "params": params,
    "error": str(e)
})

# ❌ DON'T: Log sensitive data
db.logger.info(f"User {password} logged in")  # Security risk

# 8. Configuration Management
# ✅ DO: Use environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "5432"))
}

# ❌ DON'T: Hardcode credentials
db_config = {
    "host": "prod.db.example.com",  # Avoid hardcoding
    "password": "secret123"  # Never do this
}

# 9. Query Building
# ✅ DO: Use query builders
query = (QueryBuilder(db)
    .select("name", "email")
    .from_table("users")
    .where("status = ?", "active")
    .build())

# ❌ DON'T: Concatenate strings
query = "SELECT * FROM users WHERE status = '" + status + "'"  # SQL injection risk

# 10. Performance Optimization
# ✅ DO: Use appropriate indexes
db.create_index("users", ["email"], unique=True)

# ❌ DON'T: Over-index
# Don't create indexes for every column

# 11. Data Validation
# ✅ DO: Validate data before operations
validator.validate(data)
db.insert("users", validated_data)

# ❌ DON'T: Trust input data
db.insert("users", raw_input_data)  # Risky

# 12. Deployment
# ✅ DO: Use staged deployments
# Development -> Staging -> Production

# ❌ DON'T: Deploy directly to production
# Avoid skipping staging environment
```

This completes our comprehensive documentation of PyDBConnect. The documentation covers:

1. Core functionality and extensions
2. Advanced features for production use
3. Security and compliance
4. Performance optimization
5. Best practices and anti-patterns

Would you like me to elaborate on any specific aspect or provide additional examples for any section?