# PyDBConnect

A flexible, strongly-typed database connection management library with a fluent interface for Python.

## Features

- 🔌 Support for multiple database engines (MSSQL, MySQL, PostgreSQL, SQLite, DuckDB)
- 🔒 Secure credential management through environment variables
- 🔄 Fluent interface with method chaining
- 📊 Built-in Pandas integration for data analysis
- 🎯 Type safety with runtime validation
- 🔧 Extensible design for adding new database engines

## Installation

```bash
pip install pydbconnect
```

## Quick Start

```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Connect to MSSQL
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

# Execute query and get results as PrettyTable
results = db.execute_sql_to_prettytable(
    "SELECT * FROM Customers",
    is_print=True
)
```

## Environment Setup

1. Create a `.env` file in your project root:
```env
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password
POSTGRES_USERNAME=pg_user
POSTGRES_PASSWORD=pg_pass
```

2. Set environment variable for custom location (optional):
```bash
# Windows
set DEFAULT_KEY_MANAGEMENT_ENV_FILE=path\to\your\env\file

# Unix/Linux
export DEFAULT_KEY_MANAGEMENT_ENV_FILE=path/to/your/env/file
```

## Supported Databases

### Microsoft SQL Server
```python
db = DatabaseConnection(TargetDatabaseEngine.MSSQL)
```

### PostgreSQL
```python
db = DatabaseConnection(TargetDatabaseEngine.POSTGRESQL)
```

### MySQL
```python
db = DatabaseConnection(TargetDatabaseEngine.MYSQL)
```

### SQLite
```python
db = DatabaseConnection(TargetDatabaseEngine.SQLITE3)
```

### DuckDB
```python
db = DatabaseConnection(TargetDatabaseEngine.DUCKDB)
```

## Advanced Features

### Pandas Integration
```python
# Execute query and get DataFrame
df = db.execute_sql_to_panda_dataframe(
    "SELECT * FROM Orders",
    index_column="OrderID"
)

# Convert to parquet
parquet_buffer = db.df_to_parquet_buffer(df)
```

### Connection Pooling
```python
from pydbconnect.connection import DatabaseConnection
from contextlib import contextmanager

class ConnectionPool:
    def __init__(self, engine_type, max_size=5):
        self.engine_type = engine_type
        self.max_size = max_size
        self.connections = []
        
    @contextmanager
    def get_connection(self):
        if not self.connections:
            conn = DatabaseConnection(self.engine_type).connect_to_database()
            yield conn
            conn.close()
        else:
            conn = self.connections.pop()
            yield conn
            self.connections.append(conn)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pydbconnect.git
cd pydbconnect
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

Full documentation is available at [https://pydbconnect.readthedocs.io/](https://pydbconnect.readthedocs.io/)

## Project Status

This project is in beta. While it's stable enough for production use, APIs may change between minor versions.

## Acknowledgments

- Thanks to all [contributors](CONTRIBUTORS.md)
- Built with Python's type system and modern packaging tools
- Inspired by fluent interface design patterns

---

Made with ❤️ by Me, Marko and Deepak.