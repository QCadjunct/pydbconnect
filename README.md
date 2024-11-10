# PyDBConnect

A modern, type-safe database connectivity library with support for multiple engines and advanced features.

## Features

- 🔌 Support for multiple database engines (MSSQL, MySQL, PostgreSQL, SQLite, DuckDB)
- 🔒 Secure credential management through environment variables
- 🔄 Fluent interface with method chaining
- 📊 Built-in Pandas integration for data analysis
- 🎯 Type safety with runtime validation
- 🔧 Extensible design for adding new database engines
- 🔍 Advanced query building and optimization
- 📈 Performance monitoring and metrics
- 🛡️ Data masking and encryption capabilities
- 🔄 Transaction management with savepoints
- 📝 Comprehensive audit logging
- ⚡ Connection pooling for better performance
- 🔍 Query caching and optimization
- 🚨 Automatic retry mechanisms
- 📊 Pretty table formatting for results
- 🔗 Integration with popular frameworks (FastAPI, Flask, Django)

## Quick Start

```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Create connection
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    database="myapp"
).connect_to_database()

# Execute queries with Pandas integration
df = db.execute_sql_to_dataframe("SELECT * FROM users")
```

## Installation

```bash
# Basic installation
pip install pydbconnect

# With all optional dependencies
pip install pydbconnect[all]

# Database specific installations
pip install pydbconnect[mssql]    # For MSSQL support
pip install pydbconnect[postgres] # For PostgreSQL support
pip install pydbconnect[mysql]    # For MySQL support
```

## Basic Usage

### 1. Database Connection
```python
# Simple connection with environment variables
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL
).connect_to_database()

# Custom connection parameters
db = DatabaseConnection(
    TargetDatabaseEngine.MSSQL
).finalization_of_connection_parameters(
    host="localhost",
    port=1433,
    database="Northwind"
).connect_to_database()
```

### 2. CRUD Operations
```python
# Insert data
user_id = db.insert("users", {
    "username": "john_doe",
    "email": "john@example.com"
})

# Select data
users = db.select("users", 
    columns=["username", "email"],
    where={"status": "active"}
)

# Update data
db.update("users",
    data={"status": "inactive"},
    where={"id": user_id}
)

# Delete data
db.delete("users", where={"id": user_id})
```

### 3. Transaction Management
```python
# Using context manager
with db.transaction():
    user_id = db.insert("users", {"username": "john"})
    db.insert("profiles", {"user_id": user_id})

# With savepoints
with db.transaction():
    db.savepoint("before_update")
    try:
        db.update(...)
    except:
        db.rollback_to("before_update")
```

### 4. Query Building
```python
# Using query builder
results = (db.query_builder()
    .select("users.name", "orders.total")
    .from_table("users")
    .join("orders", {"users.id": "orders.user_id"})
    .where("orders.status = ?", "completed")
    .group_by("users.name")
    .having("SUM(orders.total) > ?", 1000)
    .execute())
```

## Advanced Features

### 1. Data Masking & Security
```python
db.register_masked_fields("users", ["email", "phone"])
masked_data = db.select("users")  # Sensitive data is automatically masked
```

### 2. Performance Monitoring
```python
with db.monitor_performance() as stats:
    results = db.execute_sql_to_dataframe(complex_query)
print(f"Query took {stats.duration} seconds")
```

### 3. Connection Pooling
```python
pool = ConnectionPool(
    min_size=5,
    max_size=20,
    idle_timeout=300
)

with pool.get_connection() as conn:
    results = conn.execute_query(...)
```

## Environment Setup

Create a `.env` file:
```env
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password
POSTGRES_USERNAME=pg_user
POSTGRES_PASSWORD=pg_pass
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- 🙏 Built with modern Python features
- 💪 Inspired by the best patterns from various ORMs and database libraries
- 🌟 Contributions from the open source community

## Support

- 📚 [Documentation](https://pydbconnect.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/yourusername/pydbconnect/issues)
- 💬 [Community Chat](https://discord.gg/pydbconnect)---

Made with ❤️ by Marko, Deepak and Me.
