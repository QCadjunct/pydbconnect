# PyDBConnect

A modern, type-safe database connectivity library with support for multiple engines and advanced features.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Database Connection](#database-connection)
  - [CRUD Operations](#crud-operations)
  - [Transaction Management](#transaction-management)
  - [Query Building](#query-building)
- [Advanced Features](#advanced-features)
  - [Database Administration](#database-administration)
  - [Multi-Database Operations](#multi-database-operations)
  - [Security Features](#security-features)
  - [Performance Features](#performance-features)
  - [Framework Integration](#framework-integration)
- [Environment Setup](#environment-setup)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Support](#support)

## Features

### [Multiple Database Engines](#multiple-database-engines)

- MSSQL: Full support for Microsoft SQL Server 2016+
- MySQL: Support for MySQL 5.7+ and MariaDB
- PostgreSQL: Complete PostgreSQL 10+ compatibility
- SQLite: Embedded database support
- DuckDB: Analytical database integration

### [Secure Credential Management](#secure-credential-management)

- Environment variable-based configuration
- Encrypted credential storage
- Integration with major secret management systems
- Runtime credential rotation support

### [Fluent Interface](#fluent-interface)

- Method chaining for all operations
- Type-safe query building
- Intuitive API design
- Consistent error handling

### [Pandas Integration](#pandas-integration)

- Direct DataFrame conversions
- Native pandas data type support
- Optimized bulk operations
- DataFrame to table synchronization

### [Type Safety](#type-safety)

- Runtime type validation
- Schema enforcement
- Automatic type conversion
- Custom type mapping support

### [Extensible Design](#extensible-design)

- Plugin architecture for new engines
- Custom type adapters
- Event hooks for all operations
- Middleware support

[Previous sections remain the same...]

### [Advanced Query Building](#advanced-query-building)

- Fluent query builder interface
- Type-safe parameter binding
- Cross-database query compatibility
- Query optimization suggestions
- Complex join and subquery support

### [Performance Monitoring](#performance-monitoring)

- Real-time query performance tracking
- Connection pool statistics
- Resource utilization metrics
- Custom metric collection
- Performance reporting dashboards

### [Data Masking](#data-masking)

- Column-level encryption
- Dynamic data masking
- Role-based mask configuration
- Customizable masking patterns
- Automatic PII detection

### [Transaction Management](#transaction-management)

- ACID compliance
- Nested transaction support
- Savepoint management
- Automatic rollback
- Distributed transactions
- Transaction isolation levels

### [Audit Logging](#audit-logging)

- Comprehensive operation logging
- Query tracking
- Schema change history
- User action auditing
- Compliance reporting

### [Connection Pooling](#connection-pooling)

- Dynamic pool sizing
- Connection health monitoring
- Automatic connection recovery
- Pool statistics
- Connection lifecycle management

### [Query Caching](#query-caching)

- Intelligent result caching
- Cache invalidation strategies
- Memory-efficient storage
- Distributed cache support
- Query plan caching

### [Retry Mechanisms](#retry-mechanisms)

- Automatic retry on failure
- Configurable retry policies
- Circuit breaker pattern
- Timeout management
- Error categorization

### [Table Formatting](#table-formatting)

- Pretty print output
- Custom format templates
- Export to multiple formats
- Dynamic column sizing
- Unicode support

### [Framework Integration](#framework-integration)

- FastAPI integration
- Flask support
- Django compatibility
- SQLAlchemy interoperability
- Async framework support

### [Administrative Operations](#administrative-operations)

- Database backup and restore
- Schema management
- Index optimization
- Storage management
- Performance tuning

### [Database Optimization](#database-optimization)

- Query optimization
- Index recommendations
- Performance analysis
- Resource monitoring
- Automated maintenance

### [Cross-Database Operations](#cross-database-operations)

- Data synchronization
- Schema comparison
- Cross-database queries
- Bulk data transfer
- Type mapping

### [Engine-Specific Security](#engine-specific-security)

- Engine-specific authentication
- SSL/TLS configuration
- Role management
- Permission handling
- Security policy enforcement

### [Advanced Statistics](#advanced-statistics)

- Query performance metrics
- Resource utilization stats
- Connection analytics
- Cache hit ratios
- Performance trending

## Quick Start

### Basic Setup

```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Initialize connection
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    database="myapp",
    port=5432
).connect_to_database()

# Simple query with Pandas integration
df = db.execute_sql_to_dataframe("SELECT * FROM users")

# Basic CRUD operations
# Create
user_id = db.insert("users", {
    "username": "john_doe",
    "email": "john@example.com"
})

# Read
user = db.select("users", where={"id": user_id})

# Update
db.update("users", 
    data={"status": "active"},
    where={"id": user_id}
)

# Delete
db.delete("users", where={"id": user_id})

# Transaction management
with db.transaction():
    order_id = db.insert("orders", {"user_id": user_id, "amount": 100})
    db.update("inventory", {"stock": db.raw("stock - 1")}, {"product_id": 1})
```

### Advanced Usage

```python
# Query building
results = (db.query_builder()
    .select("users.name", "orders.total")
    .from_table("users")
    .join("orders", {"users.id": "orders.user_id"})
    .where("orders.status = ?", "completed")
    .group_by("users.name")
    .having("SUM(orders.total) > ?", 1000)
    .order_by("users.name")
    .limit(10)
    .execute())

# Data masking
db.register_masked_fields("users", {
    "email": "partial",
    "phone": "full",
    "ssn": "custom:XXX-XX-{last4}"
})

# Connection pooling
with db.get_connection_from_pool() as conn:
    results = conn.execute_query("SELECT * FROM large_table")

# Performance monitoring
with db.monitor_performance() as stats:
    results = db.execute_sql_to_dataframe("SELECT * FROM large_table")
    print(f"Query took {stats.duration} seconds")
```

[Previous sections remain the same...]

## Installation

### Basic Installation

```bash
# Basic package
pip install pydbconnect

# With development tools
pip install pydbconnect[dev]

# With testing suite
pip install pydbconnect[test]
```

### Full Installation

```bash
# All features and dependencies
pip install pydbconnect[all]
```

### Database-Specific Installation

```bash
# MSSQL support
pip install pydbconnect[mssql]

# PostgreSQL support
pip install pydbconnect[postgres]

# MySQL support
pip install pydbconnect[mysql]

# SQLite support
pip install pydbconnect[sqlite]

# DuckDB support
pip install pydbconnect[duckdb]
```

### Optional Dependencies

```bash
# Performance monitoring
pip install pydbconnect[monitoring]

# Security features
pip install pydbconnect[security]

# Framework integrations
pip install pydbconnect[frameworks]
```

## Basic Usage

### Database Connection

#### Environment Variable Configuration

```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Using environment variables
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL
).connect_to_database()
```

#### Direct Configuration

```python
# Explicit configuration
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    port=1433,
    database="Northwind",
    username="admin",
    password="secure_password"
).connect_to_database()
```

#### Connection Pool

```python
# Create connection pool
pool = ConnectionPool(
    engine_type=TargetDatabaseEngine.POSTGRESQL,
    min_size=5,
    max_size=20,
    idle_timeout=300,
    connection_params={
        "host": "localhost",
        "database": "myapp"
    }
)

# Get connection from pool
with pool.get_connection() as db:
    results = db.select("users", where={"status": "active"})
```

#### SSL/TLS Configuration

```python
# Secure connection with SSL
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL
).finalization_of_connection_parameters(
    host="secure.example.com",
    database="myapp",
    ssl_mode="verify-full",
    ssl_cert="/path/to/client-cert.pem",
    ssl_key="/path/to/client-key.pem",
    ssl_ca="/path/to/ca.pem"
).connect_to_database()
```

### CRUD Operations

#### Create Operations

```python
# Simple insert
user_id = db.insert("users", {
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": db.raw("CURRENT_TIMESTAMP")
})

# Batch insert
users = [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"}
]
db.bulk_insert("users", users, batch_size=1000)

# Insert with returning clause
user = db.insert("users",
    data={"username": "john", "email": "john@example.com"},
    returning=["id", "created_at"]
)
```

#### Read Operations

```python
# Simple select
users = db.select("users",
    columns=["id", "username", "email"],
    where={"status": "active"}
)

# Complex select
active_users = db.select("users",
    columns=["username", "email", "last_login"],
    where={
        "status": "active",
        "last_login >": "2024-01-01"
    },
    order_by=["username ASC", "last_login DESC"],
    limit=10,
    offset=20
)

# Join queries
orders = db.select(
    tables=["orders o", "users u"],
    columns=["o.id", "u.username", "o.total"],
    joins=[("users u", "u.id = o.user_id")],
    where={"o.status": "completed"}
)

# Aggregation
summary = db.select("orders",
    columns=["COUNT(*) as total_orders", "SUM(amount) as total_amount"],
    where={"status": "completed"},
    group_by=["user_id"],
    having=["SUM(amount) > 1000"]
)
```

#### Update Operations

```python
# Simple update
updated = db.update("users",
    data={"status": "inactive"},
    where={"last_login <": "2023-01-01"}
)

# Update with expressions
db.update("products",
    data={"stock": db.raw("stock - 1")},
    where={"id": 123}
)

# Batch update
updates = [
    (1, "active"),
    (2, "inactive"),
    (3, "active")
]
db.batch_update("users",
    set_columns=["status"],
    where_columns=["id"],
    values=updates
)

# Update with returning
updated_users = db.update("users",
    data={"status": "inactive"},
    where={"id": user_id},
    returning=["id", "status", "updated_at"]
)
```

#### Delete Operations

```python
# Simple delete
deleted = db.delete("users",
    where={"status": "inactive"}
)

# Complex delete
db.delete("orders",
    where={
        "status": "cancelled",
        "created_at <": "2023-01-01",
        "amount": 0
    }
)

# Delete with joins
db.delete("orders o",
    using="users u",
    where={
        "o.user_id = u.id": None,
        "u.status": "inactive"
    }
)

# Soft delete
db.update("users",
    data={
        "deleted_at": db.raw("CURRENT_TIMESTAMP"),
        "status": "deleted"
    },
    where={"id": user_id}
)
```

[Previous sections remain the same...]

### Transaction Management

#### Basic Transactions

```python
# Simple transaction
with db.transaction():
    order_id = db.insert("orders", {
        "user_id": 1,
        "total": 100.00
    })
    
    db.update("inventory",
        data={"stock": db.raw("stock - 1")},
        where={"product_id": 123}
    )

# Transaction with error handling
try:
    with db.transaction():
        db.insert("orders", {"user_id": 1, "total": 100.00})
        db.update("inventory", {"stock": db.raw("stock - 1")})
except DatabaseError as e:
    logging.error(f"Transaction failed: {e}")
```

#### Savepoints

```python
# Transaction with savepoints
with db.transaction():
    # Create first order
    order1_id = db.insert("orders", {
        "user_id": 1,
        "total": 100.00
    })
    
    # Create savepoint after first order
    db.savepoint("after_first_order")
    
    try:
        # Create second order
        order2_id = db.insert("orders", {
            "user_id": 1,
            "total": 50.00
        })
    except Exception:
        # Rollback to savepoint if second order fails
        db.rollback_to("after_first_order")
```

#### Nested Transactions

```python
# Nested transaction handling
with db.transaction():  # Outer transaction
    db.insert("users", {"username": "john"})
    
    try:
        with db.transaction():  # Nested transaction
            db.insert("orders", {"user_id": 1})
    except Exception:
        # Only the nested transaction is rolled back
        logging.error("Nested transaction failed")

    # Outer transaction continues
    db.insert("logs", {"message": "User created"})
```

#### Transaction Isolation Levels

```python
# Set isolation level
with db.transaction(isolation_level="SERIALIZABLE"):
    result = db.select("accounts",
        where={"id": account_id},
        for_update=True
    )
    
    db.update("accounts",
        data={"balance": new_balance},
        where={"id": account_id}
    )

# Read committed transaction
with db.transaction(isolation_level="READ COMMITTED"):
    results = db.select("orders", where={"status": "pending"})
```

#### Distributed Transactions

```python
# Cross-database transaction
with db.distributed_transaction(["sales_db", "inventory_db"]):
    db.execute("sales_db", """
        INSERT INTO orders (product_id, quantity)
        VALUES (?, ?)
    """, [product_id, quantity])
    
    db.execute("inventory_db", """
        UPDATE stock 
        SET quantity = quantity - ?
        WHERE product_id = ?
    """, [quantity, product_id])
```

### Query Building

#### Basic Query Building

```python
# Simple select query
query = (db.query_builder()
    .select("users.name", "users.email")
    .from_table("users")
    .where("status = ?", "active")
    .build())

# Execute built query
results = db.execute_query(query)
```

#### Complex Joins

```python
# Multiple joins with conditions
results = (db.query_builder()
    .select("u.name", "o.order_date", "p.product_name")
    .from_table("users u")
    .join("orders o", {"u.id": "o.user_id"})
    .left_join("products p", {"o.product_id": "p.id"})
    .where("o.status = ?", "completed")
    .and_where("o.order_date >= ?", "2024-01-01")
    .group_by("u.name", "o.order_date", "p.product_name")
    .having("COUNT(*) > ?", 5)
    .order_by("o.order_date DESC")
    .limit(10)
    .execute())
```

#### Subqueries

```python
# Subquery in WHERE clause
active_users = (db.query_builder()
    .select("users.name")
    .from_table("users")
    .where("users.id IN", 
        db.subquery()
            .select("user_id")
            .from_table("orders")
            .where("status = ?", "completed")
            .group_by("user_id")
            .having("COUNT(*) > ?", 5)
    )
    .execute())

# Subquery in FROM clause
summary = (db.query_builder()
    .select("dept", "AVG(order_count) as avg_orders")
    .from_subquery(
        db.subquery()
            .select("department as dept", "COUNT(*) as order_count")
            .from_table("orders")
            .group_by("department"),
        "order_stats"
    )
    .group_by("dept")
    .execute())
```

#### Window Functions

```python
# Window functions in query
rankings = (db.query_builder()
    .select(
        "department",
        "employee_name",
        "salary",
        db.window_function("RANK")
            .over()
            .partition_by("department")
            .order_by("salary DESC")
            .as_("salary_rank")
    )
    .from_table("employees")
    .execute())

# Moving averages
trends = (db.query_builder()
    .select(
        "date",
        "sales",
        db.window_function("AVG", "sales")
            .over()
            .order_by("date")
            .rows_between(-6, 0)
            .as_("weekly_avg")
    )
    .from_table("daily_sales")
    .execute())
```

#### Dynamic Query Building

```python
# Dynamic WHERE conditions
query = db.query_builder().select("*").from_table("users")

if status:
    query.where("status = ?", status)
if date_from:
    query.and_where("created_at >= ?", date_from)
if date_to:
    query.and_where("created_at <= ?", date_to)

results = query.execute()

# Dynamic ORDER BY
query = (db.query_builder()
    .select("*")
    .from_table("users"))

if sort_field:
    query.order_by(f"{sort_field} {sort_direction}")
if page_size:
    query.limit(page_size)
    query.offset((page_number - 1) * page_size)

results = query.execute()
```

### Transaction Management

#### Basic Transactions

```python
# Simple transaction
with db.transaction():
    order_id = db.insert("orders", {
        "user_id": 1,
        "total": 100.00
    })
    
    db.update("inventory",
        data={"stock": db.raw("stock - 1")},
        where={"product_id": 123}
    )

# Transaction with error handling
try:
    with db.transaction():
        db.insert("orders", {"user_id": 1, "total": 100.00})
        db.update("inventory", {"stock": db.raw("stock - 1")})
except DatabaseError as e:
    logging.error(f"Transaction failed: {e}")
```

#### Savepoints

```python
# Transaction with savepoints
with db.transaction():
    # Create first order
    order1_id = db.insert("orders", {
        "user_id": 1,
        "total": 100.00
    })
    
    # Create savepoint after first order
    db.savepoint("after_first_order")
    
    try:
        # Create second order
        order2_id = db.insert("orders", {
            "user_id": 1,
            "total": 50.00
        })
    except Exception:
        # Rollback to savepoint if second order fails
        db.rollback_to("after_first_order")
```

#### Nested Transactions

```python
# Nested transaction handling
with db.transaction():  # Outer transaction
    db.insert("users", {"username": "john"})
    
    try:
        with db.transaction():  # Nested transaction
            db.insert("orders", {"user_id": 1})
    except Exception:
        # Only the nested transaction is rolled back
        logging.error("Nested transaction failed")

    # Outer transaction continues
    db.insert("logs", {"message": "User created"})
```

#### Transaction Isolation Levels

```python
# Set isolation level
with db.transaction(isolation_level="SERIALIZABLE"):
    result = db.select("accounts",
        where={"id": account_id},
        for_update=True
    )
    
    db.update("accounts",
        data={"balance": new_balance},
        where={"id": account_id}
    )

# Read committed transaction
with db.transaction(isolation_level="READ COMMITTED"):
    results = db.select("orders", where={"status": "pending"})
```

#### Distributed Transactions

```python
# Cross-database transaction
with db.distributed_transaction(["sales_db", "inventory_db"]):
    db.execute("sales_db", """
        INSERT INTO orders (product_id, quantity)
        VALUES (?, ?)
    """, [product_id, quantity])
    
    db.execute("inventory_db", """
        UPDATE stock 
        SET quantity = quantity - ?
        WHERE product_id = ?
    """, [quantity, product_id])
```

### Query Building

#### Basic Query Building

```python
# Simple select query
query = (db.query_builder()
    .select("users.name", "users.email")
    .from_table("users")
    .where("status = ?", "active")
    .build())

# Execute built query
results = db.execute_query(query)
```

#### Complex Joins

```python
# Multiple joins with conditions
results = (db.query_builder()
    .select("u.name", "o.order_date", "p.product_name")
    .from_table("users u")
    .join("orders o", {"u.id": "o.user_id"})
    .left_join("products p", {"o.product_id": "p.id"})
    .where("o.status = ?", "completed")
    .and_where("o.order_date >= ?", "2024-01-01")
    .group_by("u.name", "o.order_date", "p.product_name")
    .having("COUNT(*) > ?", 5)
    .order_by("o.order_date DESC")
    .limit(10)
    .execute())
```

#### Subqueries

```python
# Subquery in WHERE clause
active_users = (db.query_builder()
    .select("users.name")
    .from_table("users")
    .where("users.id IN", 
        db.subquery()
            .select("user_id")
            .from_table("orders")
            .where("status = ?", "completed")
            .group_by("user_id")
            .having("COUNT(*) > ?", 5)
    )
    .execute())

# Subquery in FROM clause
summary = (db.query_builder()
    .select("dept", "AVG(order_count) as avg_orders")
    .from_subquery(
        db.subquery()
            .select("department as dept", "COUNT(*) as order_count")
            .from_table("orders")
            .group_by("department"),
        "order_stats"
    )
    .group_by("dept")
    .execute())
```

#### Window Functions

```python
# Window functions in query
rankings = (db.query_builder()
    .select(
        "department",
        "employee_name",
        "salary",
        db.window_function("RANK")
            .over()
            .partition_by("department")
            .order_by("salary DESC")
            .as_("salary_rank")
    )
    .from_table("employees")
    .execute())

# Moving averages
trends = (db.query_builder()
    .select(
        "date",
        "sales",
        db.window_function("AVG", "sales")
            .over()
            .order_by("date")
            .rows_between(-6, 0)
            .as_("weekly_avg")
    )
    .from_table("daily_sales")
    .execute())
```

#### Dynamic Query Building

```python
# Dynamic WHERE conditions
query = db.query_builder().select("*").from_table("users")

if status:
    query.where("status = ?", status)
if date_from:
    query.and_where("created_at >= ?", date_from)
if date_to:
    query.and_where("created_at <= ?", date_to)

results = query.execute()

# Dynamic ORDER BY
query = (db.query_builder()
    .select("*")
    .from_table("users"))

if sort_field:
    query.order_by(f"{sort_field} {sort_direction}")
if page_size:
    query.limit(page_size)
    query.offset((page_number - 1) * page_size)

results = query.execute()
```

[Previous sections remain the same...]

## Advanced Features

### Database Administration

#### Backup and Restore

```python
# Get admin handler for database type
admin = db.get_admin_handler()

# Full database backup
admin.backup_database(
    target_path="/backups/full_backup_20240113.bak",
    options={
        "compression": True,
        "verify": True,
        "with_logs": True
    }
)

# Differential backup
admin.backup_database(
    target_path="/backups/diff_backup_20240113.bak",
    backup_type="DIFFERENTIAL",
    options={"compression": True}
)

# Database restore
admin.restore_database(
    backup_path="/backups/full_backup_20240113.bak",
    options={
        "replace": True,
        "recovery": True,
        "verify": True
    }
)

# Point-in-time restore
admin.restore_database(
    backup_path="/backups/full_backup_20240113.bak",
    options={
        "point_in_time": "2024-01-13 14:30:00",
        "verify": True
    }
)
```

#### Database Maintenance

```python
# Analyze database statistics
stats = admin.analyze_tables(
    table_names=["users", "orders"],
    options={"verbose": True}
)

# Vacuum database
admin.vacuum_database(
    options={
        "full": True,
        "analyze": True,
        "verbose": True
    }
)

# Reindex database
admin.reindex_database(
    tables=["users", "orders"],
    options={
        "concurrent": True,
        "verbose": True
    }
)

# Update statistics
admin.update_statistics(
    tables=["users", "orders"],
    options={
        "sample_size": 1000,
        "columns": ["email", "status"]
    }
)
```

#### Performance Tuning

```python
# Get performance recommendations
recommendations = admin.analyze_performance(
    options={
        "include_indexes": True,
        "include_statistics": True,
        "include_configuration": True
    }
)

# Optimize queries
optimized_queries = admin.optimize_queries(
    queries=[
        "SELECT * FROM users WHERE status = 'active'",
        "SELECT * FROM orders WHERE created_at > '2024-01-01'"
    ],
    options={"explain": True}
)

# Monitor resource usage
metrics = admin.monitor_resources(
    duration=3600,  # 1 hour
    metrics=["cpu", "memory", "io"],
    interval=60  # 1 minute intervals
)
```

### Multi-Database Operations

#### Database Synchronization

```python
# Create multi-database connector
sync = MultiDatabaseConnector()

# Setup source and target databases
sync.attach(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=source;DATABASE=sourcedb",
    "source_db",
    "mssql"
)

sync.attach(
    "DRIVER={PostgreSQL};SERVER=target;DATABASE=targetdb",
    "target_db",
    "postgresql"
)

# Synchronize schema
sync.sync_schema(
    source="source_db",
    target="target_db",
    options={
        "include_indexes": True,
        "include_constraints": True,
        "include_triggers": True
    }
)

# Synchronize data
sync.sync_data(
    source="source_db",
    target="target_db",
    tables=["users", "orders"],
    options={
        "batch_size": 1000,
        "parallel_workers": 4,
        "validate": True
    }
)

# Real-time synchronization
sync.start_realtime_sync(
    source="source_db",
    target="target_db",
    tables=["users", "orders"],
    options={
        "poll_interval": 5,
        "batch_size": 100,
        "max_lag": 30
    }
)
```

#### Cross-Database Queries

```python
# Query across databases
results = sync.query("source_db", """
    SELECT 
        s.order_id,
        s.order_date,
        t.product_name,
        t.category
    FROM source_db.dbo.orders s
    JOIN target_db.public.products t ON s.product_id = t.id
    WHERE s.order_date >= '2024-01-01'
""")

# Aggregate across databases
summary = sync.query("source_db", """
    SELECT 
        t.category,
        COUNT(*) as order_count,
        SUM(s.amount) as total_amount
    FROM source_db.dbo.orders s
    JOIN target_db.public.products t ON s.product_id = t.id
    GROUP BY t.category
    HAVING COUNT(*) > 100
    ORDER BY total_amount DESC
""")

# Update across databases
with sync.transaction():
    sync.execute("source_db", """
        UPDATE o
        SET o.status = 'shipped'
        FROM source_db.dbo.orders o
        JOIN target_db.public.shipments s ON o.order_id = s.order_id
        WHERE s.ship_date <= CURRENT_TIMESTAMP
    """)
```

#### Data Migration

```python
# Setup migration
migration = sync.create_migration(
    source="source_db",
    target="target_db",
    options={
        "parallel_workers": 4,
        "batch_size": 1000,
        "validate": True
    }
)

# Add tables to migration
migration.add_table(
    "users",
    transformations={
        "email": lambda x: x.lower(),
        "status": lambda x: "active" if x == 1 else "inactive"
    }
)

migration.add_table(
    "orders",
    filters={
        "status": ["completed", "shipped"],
        "created_at >": "2024-01-01"
    }
)

# Execute migration
migration.execute(
    callbacks={
        "on_batch_complete": lambda count: print(f"Migrated {count} records"),
        "on_error": lambda err: logging.error(f"Migration error: {err}")
    }
)
```

### Security Features

#### Data Masking

```python
# Configure data masking rules
db.configure_masking({
    "users": {
        "email": {
            "type": "partial",
            "show_first": 3,
            "show_last": 2,
            "mask_char": "*"
        },
        "phone": {
            "type": "pattern",
            "pattern": "XXX-XXX-{last4}",
            "preserve_format": True
        },
        "ssn": {
            "type": "full",
            "mask_char": "#"
        },
        "address": {
            "type": "custom",
            "function": lambda addr: f"{addr.split()[0]}... {addr.split()[-1]}"
        }
    },
    "payment_methods": {
        "card_number": {
            "type": "pattern",
            "pattern": "XXXX-XXXX-XXXX-{last4}"
        }
    }
})

# Query with masking
masked_users = db.select(
    "users",
    columns=["id", "email", "phone", "ssn", "address"],
    masking=True
)

# Role-based masking
db.configure_masking_roles({
    "admin": {
        "mask_level": "none",
        "tables": ["*"]
    },
    "support": {
        "mask_level": "partial",
        "tables": ["users", "orders"]
    },
    "analyst": {
        "mask_level": "full",
        "tables": ["payment_methods"]
    }
})

# Query with role-based masking
with db.as_role("support"):
    users = db.select("users", masking=True)
```

#### Encryption

```python
# Configure encryption settings
db.configure_encryption({
    "algorithm": "AES-256-GCM",
    "key_rotation_interval": "30d",
    "key_store": "vault",
    "key_store_config": {
        "url": "https://vault.example.com",
        "role": "db-encryption"
    }
})

# Enable column encryption
db.encrypt_columns("users", {
    "ssn": {
        "type": "deterministic",
        "searchable": True
    },
    "bank_account": {
        "type": "randomized",
        "searchable": False
    }
})

# Query with automatic decryption
users = db.select(
    "users",
    columns=["id", "ssn", "bank_account"],
    decrypt=True
)

# Selective decryption
users = db.select(
    "users",
    columns=["id", "ssn", "bank_account"],
    decrypt_columns=["ssn"]
)

# Encryption key rotation
db.rotate_encryption_keys(
    tables=["users"],
    columns=["ssn", "bank_account"]
)
```

#### Audit Logging

```python
# Configure audit logging
db.configure_audit({
    "level": "detailed",
    "log_queries": True,
    "log_changes": True,
    "log_access": True,
    "retention_period": "90d",
    "exclude_tables": ["logs", "metrics"]
})

# Start audit session
with db.audit_session(user="john_doe", application="web_app"):
    # All operations within this block are audited
    db.update("users",
        data={"status": "inactive"},
        where={"id": user_id}
    )

# Query audit logs
audit_logs = db.query_audit_logs(
    start_date="2024-01-01",
    end_date="2024-01-31",
    filters={
        "user": "john_doe",
        "operation_type": ["UPDATE", "DELETE"],
        "table": "users"
    }
)

# Export audit report
db.export_audit_report(
    format="pdf",
    period="monthly",
    include_summary=True,
    output_path="/reports/audit_2024_01.pdf"
)
```

### Performance Features

#### Connection Pooling

```python
# Create connection pool
pool = ConnectionPool(
    min_size=5,
    max_size=20,
    idle_timeout=300,
    max_lifetime=3600,
    validation_query="SELECT 1",
    validation_interval=60,
    on_connect=lambda conn: conn.execute("SET search_path TO myapp"),
    on_disconnect=lambda conn: conn.close()
)

# Get connection with automatic return
with pool.get_connection() as conn:
    results = conn.select("users", where={"status": "active"})

# Get connection with manual management
conn = pool.get_connection()
try:
    results = conn.select("users", where={"status": "active"})
finally:
    pool.return_connection(conn)

# Monitor pool status
stats = pool.get_stats()
print(f"Active connections: {stats.active_connections}")
print(f"Idle connections: {stats.idle_connections}")
print(f"Waiting requests: {stats.waiting_requests}")
print(f"Total connections: {stats.total_connections}")
```

#### Query Caching

```python
# Configure query cache
cache = QueryCache(
    backend="redis",
    ttl=300,  # 5 minutes
    max_size="1GB",
    serializer="msgpack",
    config={
        "host": "redis.example.com",
        "port": 6379
    }
)

# Enable caching for specific queries
@cache.cached(ttl=600)  # 10 minutes
def get_user_stats(status: str) -> Dict:
    return db.select(
        "users",
        columns=["COUNT(*) as count", "AVG(age) as avg_age"],
        where={"status": status}
    )

# Cache invalidation
cache.invalidate(
    tables=["users"],
    keys=["user_stats", "user_list"]
)

# Cache warming
cache.warm_up([
    ("user_stats", {"status": "active"}),
    ("user_stats", {"status": "inactive"}),
])

# Cache monitoring
stats = cache.get_stats()
print(f"Hit ratio: {stats.hit_ratio}")
print(f"Miss ratio: {stats.miss_ratio}")
print(f"Memory usage: {stats.memory_usage}")
```

[Previous sections remain the same...]

### Framework Integration

#### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from pydbconnect.integrations import DatabaseSession, FastAPIIntegration
from typing import List

app = FastAPI()
db_integration = FastAPIIntegration()

# Initialize database integration
@app.on_event("startup")
async def startup():
    await db_integration.initialize(
        engine_type="postgresql",
        connection_params={
            "host": "localhost",
            "database": "myapp",
            "username": "user",
            "password": "pass"
        },
        pool_settings={
            "min_size": 5,
            "max_size": 20
        }
    )

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown():
    await db_integration.cleanup()

# Database dependency
async def get_db():
    async with db_integration.session() as db:
        yield db

# API Routes
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: DatabaseSession = Depends(get_db)):
    try:
        user = await db.select("users", where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/")
async def create_user(user: dict, db: DatabaseSession = Depends(get_db)):
    try:
        async with db.transaction():
            user_id = await db.insert("users", user)
            return {"id": user_id, **user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch operations
@app.post("/users/batch")
async def create_users(users: List[dict], db: DatabaseSession = Depends(get_db)):
    try:
        async with db.transaction():
            results = await db.bulk_insert("users", users)
            return {"created": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Flask Integration

```python
from flask import Flask, request, jsonify
from pydbconnect.integrations import FlaskDatabasePlugin

app = Flask(__name__)
db = FlaskDatabasePlugin(app)

# Configure database
app.config['DATABASE'] = {
    'engine': 'postgresql',
    'host': 'localhost',
    'database': 'myapp',
    'username': 'user',
    'password': 'pass',
    'pool_size': 10
}

# Request handlers
@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def teardown_request(exception=None):
    db.disconnect()

# Routes
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = db.select("users", 
            where={"status": "active"},
            order_by=["username"]
        )
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        with db.transaction():
            user_id = db.insert("users", data)
            return jsonify({"id": user_id, **data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Custom commands
@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    db.init_db()
    print("Initialized the database.")
```

#### Django Integration

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'pydbconnect.django',
        'NAME': 'myapp',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'pool_size': 10,
            'max_overflow': 5,
            'pool_timeout': 30,
        }
    }
}

# models.py
from django.db import models
from pydbconnect.django import PyDBModel

class User(PyDBModel):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'users'
    
    @classmethod
    def active_users(cls):
        return cls.objects.filter(status='active')
    
    def deactivate(self):
        with transaction.atomic():
            self.status = 'inactive'
            self.save()

# views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import User

def user_list(request):
    users = User.objects.all()
    data = [{'id': user.id, 'username': user.username} 
            for user in users]
    return JsonResponse(data, safe=False)

def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'status': user.status
    })
```

## Environment Setup

### Environment Variables

```env
# Database Connections
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password
POSTGRES_USERNAME=pg_user
POSTGRES_PASSWORD=pg_pass
MYSQL_USERNAME=mysql_user
MYSQL_PASSWORD=mysql_pass

# Connection Settings
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=30
DB_CONNECT_TIMEOUT=10

# Security Settings
DB_ENCRYPTION_KEY=your-encryption-key
DB_SSL_MODE=verify-full
DB_SSL_CERT_PATH=/path/to/cert.pem
DB_SSL_KEY_PATH=/path/to/key.pem
DB_SSL_CA_PATH=/path/to/ca.pem

# Monitoring Settings
DB_MONITOR_ENABLED=true
DB_METRICS_PORT=9090
DB_LOG_LEVEL=INFO

# Cache Settings
CACHE_BACKEND=redis
CACHE_HOST=localhost
CACHE_PORT=6379
CACHE_TTL=300

# Framework Specific
DJANGO_DB_ENGINE=pydbconnect.django
FLASK_DB_PLUGIN=pydbconnect.flask
FASTAPI_DB_MODULE=pydbconnect.fastapi
```

### Configuration File

```yaml
# config.yaml
database:
  default:
    engine: postgresql
    host: localhost
    port: 5432
    database: myapp
    pool:
      min_size: 5
      max_size: 20
      timeout: 30
    ssl:
      mode: verify-full
      cert: /path/to/cert.pem
      key: /path/to/key.pem
      ca: /path/to/ca.pem

  replica:
    engine: postgresql
    host: replica.example.com
    port: 5432
    database: myapp
    pool:
      min_size: 2
      max_size: 10
    
security:
  encryption:
    algorithm: AES-256-GCM
    key_rotation: 30d
    key_store: vault
  
  masking:
    default_level: partial
    roles:
      admin: none
      support: partial
      analyst: full

monitoring:
  enabled: true
  metrics_port: 9090
  log_level: INFO
  retention: 30d
  exporters:
    - prometheus
    - elasticsearch

cache:
  backend: redis
  host: localhost
  port: 6379
  ttl: 300
  max_size: 1GB
```

[Previous sections remain the same...]

## Contributing

### Development Setup

#### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/pydbconnect.git
cd pydbconnect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Development Dependencies

```bash
# Install all development dependencies
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
```

#### 3. Set Up Development Databases

```bash
# Docker compose for development databases
docker-compose up -d postgres mysql mssql

# Create test databases
python scripts/setup_test_dbs.py
```

### Running Tests

#### Unit Tests

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_connection.py

# Run with coverage
pytest --cov=pydbconnect tests/

# Generate coverage report
coverage html
```

#### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run specific database integration tests
pytest tests/integration/test_postgresql.py
pytest tests/integration/test_mysql.py
pytest tests/integration/test_mssql.py
```

#### Performance Tests

```bash
# Run performance benchmarks
pytest tests/performance/

# Run specific benchmark
pytest tests/performance/test_connection_pool.py
```

### Code Style and Quality

#### Code Formatting

```bash
# Format code with black
black pydbconnect/

# Sort imports
isort pydbconnect/

# Format all files
make format
```

#### Type Checking

```bash
# Run mypy type checker
mypy pydbconnect/

# Run with strict mode
mypy --strict pydbconnect/
```

#### Linting

```bash
# Run flake8
flake8 pydbconnect/

# Run pylint
pylint pydbconnect/

# Run all quality checks
make lint
```

### Documentation

#### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# Serve documentation locally
python -m http.server --directory _build/html
```

#### Writing Documentation

```bash
# Create new documentation page
cd docs/source
touch new_feature.rst

# Update API documentation
sphinx-apidoc -o source/ ../pydbconnect
```

### Submitting Changes

#### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Create bugfix branch
git checkout -b fix/bug-description
```

#### 2. Make Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add amazing feature"
git commit -m "fix: resolve connection pool issue"
```

#### 3. Push and Create PR

```bash
# Push changes
git push origin feature/amazing-feature

# Create PR through GitHub interface
# Include detailed description and test results
```

## License

MIT License

Copyright (c) 2024 PyDBConnect Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

### Core Team

- 👨‍💻 Peter Heller (Me)
- 👨‍💻 Marko
- 👨‍💻 Deepak


### Special Thanks for a little help from my friends (Joe Cocker https://www.dailymotion.com/video/x2p98e5)

- 🙏 The DuckDB team for inspiration on multi-database operations
- 🙏 The SQLAlchemy community for query building patterns
- 🙏 The FastAPI team for async database patterns
- 🙏 All our open source contributors

### Built With

- 🐍 Modern Python features and type hints
- 💪 Best practices from various ORMs and database libraries
- 🔒 Industry standard security patterns
- 📊 Advanced database optimization techniques

## Support

### PyDBConnect Documentation

- 📚 [Full Documentation](https://pydbconnect.readthedocs.io/)
- 📖 [API Reference](https://pydbconnect.readthedocs.io/en/latest/api.html)
- 🎓 [Tutorials](https://pydbconnect.readthedocs.io/en/latest/tutorials/)
- 📋 [Examples](https://pydbconnect.readthedocs.io/en/latest/examples/)
- 📑 [Migration Guides](https://pydbconnect.readthedocs.io/en/latest/migration/)

### Getting Help

- 🐛 [Issue Tracker](https://github.com/yourusername/pydbconnect/issues)
- 💬 [Discord Community](https://discord.gg/pydbconnect)
- 📧 [Email Support](mailto:support@pydbconnect.com)
- 📝 [Stack Overflow](https://stackoverflow.com/questions/tagged/pydbconnect)

### Commercial Support

- 💼 [Enterprise Plans](https://pydbconnect.com/enterprise)
- 👥 [Training & Consulting](https://pydbconnect.com/consulting)
- 🤝 [Partnership Opportunities](https://pydbconnect.com/partners)
- 📞 [Direct Support Line](tel:+1234567890)

### Updates & News

- 📰 [Blog](https://pydbconnect.com/blog)
- 🐦 [Twitter](https://twitter.com/pydbconnect)
- 📬 [Newsletter](https://pydbconnect.com/newsletter)
- 📱 [RSS Feed](https://pydbconnect.com/feed)

---

Made with ❤️ by Marko, Deepak and Me.
