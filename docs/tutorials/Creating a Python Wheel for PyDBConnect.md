# Creating a Python Wheel for PyDBConnect

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Required Files](#required-files)
4. [Setup Configuration](#setup-configuration)
5. [Core Features](#core-features)
6. [Building the Wheel](#building-the-wheel)
7. [Testing the Wheel](#testing-the-wheel)
8. [Publishing to PyPI](#publishing-to-pypi)
9. [Advanced Configuration](#advanced-configuration)

## Overview

PyDBConnect provides a powerful multi-database connectivity solution with features similar to DuckDB's ATTACH functionality. It enables:

- 🔌 Multi-database connectivity
- 🔄 Transaction management
- 📊 Data migration between databases
- 🔍 Cross-database queries
- 🛡️ Type-safe operations

### What is a Python Wheel?
- 🎡 A built-package format for Python
- 📦 Contains all necessary files for installation
- 🚀 Faster installation than source distributions
- ✨ Pre-built binaries when applicable

## Project Structure

```plaintext
pydbconnect/
├── src/
│   └── pydbconnect/
│       ├── __init__.py
│       ├── connection.py
│       ├── multi_database_connector.py  # New multi-database support
│       ├── descriptors.py
│       ├── exceptions.py
│       ├── utils.py
│       └── db_constants/
│           ├── __init__.py
│           ├── enum_connection_constants.py
│           └── database_connection_constants.py
├── tests/
│   ├── __init__.py
│   ├── test_connection.py
│   ├── test_multi_database.py          # New tests
│   └── test_utils.py
├── docs/
│   ├── index.md
│   └── multi_database.md               # New documentation
├── examples/
│   └── multi_database_example.py       # Usage examples
├── LICENSE
├── README.md
├── pyproject.toml
├── setup.cfg
└── setup.py
```

## Core Features

### Multi-Database Support
```python
from pydbconnect import MultiDatabaseConnector

# Create connector
mdb = MultiDatabaseConnector()

# Attach multiple databases
mdb.attach(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server1;DATABASE=db1;UID=user;PWD=pass",
    "mssql_db",
    "mssql"
)

mdb.attach(
    "DRIVER={MySQL ODBC 8.0 Driver};SERVER=server2;DATABASE=db2;UID=user;PWD=pass",
    "mysql_db",
    "mysql"
)
```

### Transaction Management
```python
with mdb.transaction():
    # Create table
    mdb.execute("mssql_db", """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100)
        )
    """)
    
    # Insert data
    mdb.execute("mssql_db", """
        INSERT INTO users (id, name) 
        VALUES (1, 'Test User')
    """)
```

### Data Migration
```python
# Copy table between databases
mdb.copy_table(
    source_db="mysql_db",
    target_db="mssql_db",
    table_name="users",
    batch_size=1000
)
```

## Required Files

### 1. pyproject.toml
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
write_to = "src/pydbconnect/_version.py"

[project]
name = "pydbconnect"
description = "Modern multi-database connectivity library"
requires-python = ">=3.8"
dependencies = [
    "pandas>=1.3.0",
    "pyodbc>=4.0.30",
    "psycopg2-binary>=2.9.0",
    "prettytable>=2.0.0",
    "python-dotenv>=0.19.0"
]

[project.optional-dependencies]
mssql = ["pyodbc>=4.0.30"]
mysql = ["mysql-connector-python>=8.0.26"]
postgres = ["psycopg2-binary>=2.9.0"]
all = [
    "pyodbc>=4.0.30",
    "mysql-connector-python>=8.0.26",
    "psycopg2-binary>=2.9.0"
]
```

### 2. setup.cfg
```ini
[metadata]
name = pydbconnect
description = Modern multi-database connectivity library with ATTACH-like functionality
long_description = file: README.md
long_description_content_type = text/markdown
author = Your Name
author_email = your.email@example.com
license = MIT
license_files = LICENSE
platforms = any
classifiers =
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent
    Programming Language :: Python
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Topic :: Database
    Topic :: Software Development :: Libraries

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.8

[options.packages.find]
where = src
```

## Testing the Wheel

### 1. Installation Test Script
```python
# test_installation.py
from pydbconnect import MultiDatabaseConnector

def test_multi_database():
    # Create connector
    mdb = MultiDatabaseConnector()
    
    try:
        # Attach test databases
        mdb.attach(
            "DRIVER={SQLite3};Database=test1.db",
            "db1",
            "sqlite"
        )
        
        mdb.attach(
            "DRIVER={SQLite3};Database=test2.db",
            "db2",
            "sqlite"
        )
        
        # Test operations
        with mdb.transaction():
            mdb.execute("db1", """
                CREATE TABLE test (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """)
            
            mdb.execute("db1", """
                INSERT INTO test (value) 
                VALUES ('test data')
            """)
        
        # Test query
        result = mdb.query("db1", "SELECT * FROM test")
        assert len(result) > 0
        
        print("Installation test successful!")
        
    finally:
        mdb.close()

if __name__ == "__main__":
    test_multi_database()
```

### 2. Integration Tests
```python
# tests/test_multi_database.py
import pytest
from pydbconnect import MultiDatabaseConnector

class TestMultiDatabaseConnector:
    @pytest.fixture
    def mdb(self):
        connector = MultiDatabaseConnector()
        yield connector
        connector.close()
    
    def test_attach_database(self, mdb):
        mdb.attach(
            "DRIVER={SQLite3};Database=:memory:",
            "test_db",
            "sqlite"
        )
        assert "test_db" in mdb.databases
    
    def test_transaction_management(self, mdb):
        mdb.attach(
            "DRIVER={SQLite3};Database=:memory:",
            "test_db",
            "sqlite"
        )
        
        with mdb.transaction():
            mdb.execute("test_db", """
                CREATE TABLE test (id INTEGER PRIMARY KEY)
            """)
        
        result = mdb.query("test_db", """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='test'
        """)
        assert len(result) == 1
```

## Advanced Usage Examples

### 1. Data Migration Pipeline
```python
def migrate_data(source_conn: str, target_conn: str, tables: List[str]):
    mdb = MultiDatabaseConnector()
    
    try:
        # Attach databases
        mdb.attach(source_conn, "source", "source_type")
        mdb.attach(target_conn, "target", "target_type")
        
        # Migrate each table
        for table in tables:
            print(f"Migrating table: {table}")
            mdb.copy_table("source", "target", table)
            
        print("Migration complete!")
        
    finally:
        mdb.close()
```

### 2. Cross-Database Analysis
```python
def analyze_sales():
    mdb = MultiDatabaseConnector()
    
    try:
        # Attach databases
        mdb.attach("sales_conn_str", "sales", "mssql")
        mdb.attach("inventory_conn_str", "inventory", "mysql")
        
        # Cross-database query
        results = mdb.query("sales", """
            SELECT 
                s.order_id,
                s.product_id,
                s.quantity,
                i.stock_level
            FROM sales.dbo.orders s
            JOIN inventory.dbo.products i 
                ON s.product_id = i.id
            WHERE s.order_date >= '2024-01-01'
        """)
        
        return results
        
    finally:
        mdb.close()
```

# PyDBConnect: Advanced Deployment and Testing

## Deployment Examples

### 1. Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.10-slim

# Install database drivers
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install ODBC drivers
ADD mssql-driver-install.sh /tmp/
RUN chmod +x /tmp/mssql-driver-install.sh && /tmp/mssql-driver-install.sh

# Install PyDBConnect
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add application code
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

```bash
# mssql-driver-install.sh
#!/bin/bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### 2. Kubernetes Deployment
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pydbconnect-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pydbconnect
  template:
    metadata:
      labels:
        app: pydbconnect
    spec:
      containers:
      - name: pydbconnect
        image: pydbconnect:latest
        envFrom:
        - secretRef:
            name: database-credentials
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
```

```yaml
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
type: Opaque
stringData:
  MSSQL_CONNECTION: "Driver={ODBC Driver 17 for SQL Server};Server=server1;Database=db1;Uid=user;Pwd=pass"
  MYSQL_CONNECTION: "Driver={MySQL ODBC 8.0 Driver};Server=server2;Database=db2;Uid=user;Pwd=pass"
```

## CI/CD Configurations

### 1. GitHub Actions
```yaml
# .github/workflows/build-test-deploy.yml
name: Build, Test, and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
        database: [mssql, mysql, postgresql]

    services:
      mssql:
        image: mcr.microsoft.com/mssql/server:2019-latest
        env:
          ACCEPT_EULA: Y
          SA_PASSWORD: YourStrong!Passw0rd
        ports:
          - 1433:1433

      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test
        ports:
          - 3306:3306

      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev,test,${{ matrix.database }}]
        
    - name: Run tests
      run: |
        pytest tests/ --database=${{ matrix.database }}
        
    - name: Build wheel
      if: matrix.python-version == '3.10' && matrix.database == 'postgresql'
      run: |
        python -m build
        
    - name: Upload wheel
      if: matrix.python-version == '3.10' && matrix.database == 'postgresql'
      uses: actions/upload-artifact@v2
      with:
        name: dist
        path: dist/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/download-artifact@v2
      with:
        name: dist
        path: dist/
        
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload dist/*
```

### 2. GitLab CI
```yaml
# .gitlab-ci.yml
image: python:3.10

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/

stages:
  - test
  - build
  - deploy

test:
  stage: test
  services:
    - mssql:2019-latest
    - mysql:8.0
    - postgres:13
  script:
    - pip install -e .[dev,test,all]
    - pytest tests/

build:
  stage: build
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  script:
    - pip install twine
    - twine upload dist/*
  only:
    - tags
```

## Advanced Testing Scenarios

### 1. Performance Tests
```python
# tests/test_performance.py
import pytest
import time
from pydbconnect import MultiDatabaseConnector

class TestPerformance:
    @pytest.fixture
    def large_dataset(self):
        """Generate large test dataset."""
        return [
            {"id": i, "value": f"test_{i}"}
            for i in range(100000)
        ]
    
    def test_bulk_insert_performance(self, large_dataset):
        mdb = MultiDatabaseConnector()
        try:
            mdb.attach("connection_string", "test_db", "sqlite")
            
            # Measure insertion time
            start_time = time.time()
            
            with mdb.transaction():
                mdb.execute("test_db", """
                    CREATE TABLE test (
                        id INTEGER PRIMARY KEY,
                        value TEXT
                    )
                """)
                
                # Test different batch sizes
                batch_sizes = [100, 1000, 10000]
                for batch_size in batch_sizes:
                    mdb.copy_table(
                        source_data=large_dataset[:10000],
                        target_db="test_db",
                        table_name="test",
                        batch_size=batch_size
                    )
            
            execution_time = time.time() - start_time
            assert execution_time < 30  # Performance threshold
            
        finally:
            mdb.close()

    def test_query_performance(self):
        mdb = MultiDatabaseConnector()
        try:
            # Setup test databases
            mdb.attach("db1_conn", "db1", "sqlite")
            mdb.attach("db2_conn", "db2", "sqlite")
            
            # Test cross-database query performance
            start_time = time.time()
            
            results = mdb.query("db1", """
                SELECT d1.*, d2.value as related_value
                FROM db1.test d1
                JOIN db2.test d2 ON d1.id = d2.id
                WHERE d1.id < 1000
            """)
            
            query_time = time.time() - start_time
            assert query_time < 5  # Performance threshold
            
        finally:
            mdb.close()
```

### 2. Load Tests
```python
# tests/test_load.py
import concurrent.futures
import pytest
from pydbconnect import MultiDatabaseConnector

class TestLoad:
    def test_concurrent_connections(self):
        def worker(i):
            mdb = MultiDatabaseConnector()
            try:
                mdb.attach("connection_string", f"db_{i}", "sqlite")
                return True
            except Exception as e:
                return False
            finally:
                mdb.close()
        
        # Test with 100 concurrent connections
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            results = list(executor.map(worker, range(100)))
            
        assert all(results)

    def test_connection_pool_under_load(self):
        def query_worker(mdb, i):
            try:
                result = mdb.query(f"db_{i % 2}", "SELECT 1")
                return True
            except Exception:
                return False
        
        mdb = MultiDatabaseConnector()
        try:
            # Attach test databases
            mdb.attach("db1_conn", "db_0", "sqlite")
            mdb.attach("db2_conn", "db_1", "sqlite")
            
            # Run 1000 queries across 10 threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(query_worker, mdb, i)
                    for i in range(1000)
                ]
                results = [f.result() for f in futures]
                
            assert all(results)
            
        finally:
            mdb.close()
```

## Database-Specific Optimizations

### 1. MSSQL Optimizations
```python
class MSSQLOptimizer:
    @staticmethod
    def optimize_connection_string(conn_str: str) -> str:
        """Optimize MSSQL connection string parameters."""
        params = {
            "MultipleActiveResultSets": "True",
            "Pooling": "True",
            "Min Pool Size": "5",
            "Max Pool Size": "100",
            "Connect Timeout": "30",
            "ApplicationIntent": "ReadWrite"
        }
        
        return conn_str + ";" + ";".join(f"{k}={v}" for k, v in params.items())

    @staticmethod
    def optimize_query(query: str) -> str:
        """Add MSSQL-specific query hints."""
        if query.lower().startswith("select"):
            return f"""
            SET ARITHABORT ON;
            SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
            {query}
            OPTION (OPTIMIZE FOR UNKNOWN)
            """
        return query
```

### 2. MySQL Optimizations
```python
class MySQLOptimizer:
    @staticmethod
    def optimize_connection_string(conn_str: str) -> str:
        """Optimize MySQL connection string parameters."""
        params = {
            "pooling": "true",
            "max_pool_size": "100",
            "default_command_timeout": "30",
            "connection_timeout": "30",
            "connection_lifetime": "0",
            "auto_enlist": "true"
        }
        
        return conn_str + ";" + ";".join(f"{k}={v}" for k, v in params.items())

    @staticmethod
    def optimize_query(query: str) -> str:
        """Add MySQL-specific query hints."""
        if query.lower().startswith("select"):
            return f"""
            SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
            {query}
            """
        return query
```

### 3. PostgreSQL Optimizations
```python
class PostgreSQLOptimizer:
    @staticmethod
    def optimize_connection_string(conn_str: str) -> str:
        """Optimize PostgreSQL connection string parameters."""
        params = {
            "pooling": "true",
            "MinPoolSize": "5",
            "MaxPoolSize": "100",
            "ConnectionLifeTime": "15",
            "ConnectionIdleLifetime": "300",
            "ApplicationName": "PyDBConnect"
        }
        
        return conn_str + ";" + ";".join(f"{k}={v}" for k, v in params.items())

    @staticmethod
    def optimize_query(query: str) -> str:
        """Add PostgreSQL-specific query hints."""
        if query.lower().startswith("select"):
            return f"""
            SET LOCAL statement_timeout = '30s';
            SET LOCAL work_mem = '64MB';
            {query}
            """
        return query
```

Would you like me to:
1. Add monitoring and observability examples?
2. Include more deployment scenarios?
3. Add security hardening examples?
4. Include high availability configurations?