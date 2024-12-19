# 🔄 Complete Python Database Connector Guide

## 📑 Table of Contents

1. [Architecture Overview](#architecture)
2. [Configuration Setup](#config)
3. [Debugging System](#debug)
4. [Testing Framework](#testing)
5. [Code Examples](#examples)
6. [Troubleshooting](#troubleshoot)

## 🏗️ Architecture Overview {#architecture}

### Complete Project Structure

```mermaidhttps://github.com/NVIDIA
graph TD
    subgraph Project_Root[Project Root Directory]
        A[pyproject.toml] --> B[core/]
        A --> C[templates/]
        A --> D[utils/]
        A --> E[tests/]
        A --> F[.vscode/]
        
        subgraph VS_Code_Config[VS Code Configuration]
            F --> J[launch.json]
            F --> K[settings.json]
        end
        
        subgraph Core_Components[Core Components]
            B --> G[connector.py]
            B --> H[examples/]
            H --> I1[mssql_demo.py]
            H --> I2[advanced_demo.py]
            H --> I3[error_handling_demo.py]
        end
        
        subgraph Test_Components[Test Components]
            E --> L[example_poc modules/]
            L --> O1[test_connection.py]
            L --> O2[test_queries.py]
            L --> O3[test_error_handling.py]
        end
    end
```

### System Integration Flow

```mermaid
graph LR
    subgraph Config_Files[Configuration]
        A[settings.json]
        B[launch.json]
        C[pyproject.toml]
        D[.env]
    end

    subgraph Runtime[Runtime Environment]
        E[VS Code]
        F[Python Interpreter]
        G[Debug Adapter]
    end

    subgraph Execution[Execution Layer]
        H[Database Connector]
        I[Test Framework]
        J[Examples]
    end

    A --> E
    B --> G
    C --> F
    D --> H
    E --> H
    G --> I
    H --> J

## 🧪 Testing Examples

### 1. Basic Connection Test
```python
# tests/example_poc modules/test_connection.py
"""Test database connection functionality."""

import pytest
from core.connector import DatabaseConnector, DatabaseError
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)

def test_mssql_connection():
    """Test basic MSSQL connection."""
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )
    
    with (
        db.set_credentials_based_on_connect_option()
        .finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=13001,
            DATABASE_NAME="AdventureWorks2019",
        )
        .connect_to_database()
    ) as conn:
        result = conn.execute_query_to_dataframe("SELECT @@VERSION as Version")
        assert not result.empty
        assert "Version" in result.columns

def test_connection_error_handling():
    """Test connection error scenarios."""
    with pytest.raises(DatabaseError):
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )
        
        with (
            db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(
                DRIVER="{ODBC Driver 17 for SQL Server}",
                SERVER="invalid_server",
                PORT_NUMBER=13001,
                DATABASE_NAME="AdventureWorks2019",
            )
            .connect_to_database()
        ):
            pass
```

### 2. Query Testing

```python
# tests/example_poc modules/test_queries.py
"""Test database query functionality."""

import pytest
import pandas as pd
from core.connector import DatabaseConnector
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)

@pytest.fixture
def db_connection():
    """Provide a database connection fixture."""
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )
    
    with (
        db.set_credentials_based_on_connect_option()
        .finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=13001,
            DATABASE_NAME="AdventureWorks2019",
        )
        .connect_to_database()
    ) as conn:
        yield conn

def test_dataframe_query(db_connection):
    """Test DataFrame query execution."""
    query = """
    SELECT TOP 5
        ProductID,
        Name,
        ProductNumber
    FROM Production.Product
    """
    df = db_connection.execute_query_to_dataframe(query)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert all(col in df.columns for col in ['ProductID', 'Name', 'ProductNumber'])

def test_prettytable_query(db_connection):
    """Test PrettyTable query execution."""
    query = "SELECT @@VERSION as Version"
    table = db_connection.execute_query_to_prettytable(query, print_result=False)
    assert table is not None
    assert 'Version' in table.field_names
```

### 3. Error Handling Test

```python
# tests/example_poc modules/test_error_handling.py
"""Test error handling scenarios."""

import pytest
from core.connector import DatabaseConnector, DatabaseError, ConnectionError
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)

@pytest.mark.parametrize("test_input,expected_exception", [
    ({"SERVER": "invalid_server"}, ConnectionError),
    ({"DATABASE_NAME": "invalid_db"}, DatabaseError),
    ({"PORT_NUMBER": 9999}, ConnectionError),
])
def test_connection_errors(test_input, expected_exception):
    """Test various connection error scenarios."""
    with pytest.raises(expected_exception):
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )
        
        params = {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "SERVER": "127.0.0.1",
            "PORT_NUMBER": 13001,
            "DATABASE_NAME": "AdventureWorks2019",
        }
        params.update(test_input)
        
        with (
            db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(**params)
            .connect_to_database()
        ):
            pass

def test_query_errors(db_connection):
    """Test query execution errors."""
    with pytest.raises(DatabaseError):
        db_connection.execute_query_to_dataframe(
            "SELECT * FROM NonExistentTable"
        )

def test_transaction_rollback():
    """Test transaction rollback on error."""
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )
    
    with (
        db.set_credentials_based_on_connect_option()
        .finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=13001,
            DATABASE_NAME="AdventureWorks2019",
        )
        .connect_to_database()
    ) as conn:
        try:
            conn.execute_statement("BEGIN TRANSACTION")
            conn.execute_statement("INSERT INTO InvalidTable VALUES (1)")
        except DatabaseError:
            conn.execute_statement("ROLLBACK")
            # Verify rollback worked
            assert True  # Add appropriate verification
        else:
            assert False, "Expected DatabaseError was not raised"
```
