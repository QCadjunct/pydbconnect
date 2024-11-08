# Test Cases Documentation

## 1. Unit Tests

### 1.1 Connection Tests
### 6.2 Common Validation Errors### 6.2 Common Validation Errors

- Missing required parameters
- Invalid port numbers
- Invalid hostnames/IPs
- Invalid database names
- Invalid credentials
- Dangerous SQL patterns
- Parameter count mismatches
- Invalid DataFrame operations

## 7. Best Practices

1. Always validate connection parameters before attempting connection
2. Use parameterized queries instead of string concatenation
3. Validate credentials when authentication is required
4. Validate DataFrame operations before processing
5. Handle validation errors appropriately
6. Log validation failures for debugging
7. Use type hints for better code clarity
8. Keep validation rules updated with security best practices

    - Missing required parameters
    - Invalid port numbers
    - Invalid hostnames/IPs
    - Invalid database names
    - Invalid credentials
    - Dangerous SQL patterns
    - Parameter count mismatches
    - Invalid DataFrame operations

## 7. Best Practices

1. Always validate connection parameters before attempting connection
2. Use parameterized queries instead of string concatenation
3. Validate credentials when authentication is required
4. Validate DataFrame operations before processing
5. Handle validation errors appropriately
6. Log validation failures for debugging
7. Use type hints for better code clarity
8. Keep validation rules updated with security best practices
  
# tests/test_connection.py
import pytest
from pydatabaseconnection import DatabaseConnection
from pydatabaseconnection.types.exceptions import DatabaseConnectionError

class TestDatabaseConnection:
    def test_basic_connection(self):
        """Test basic connection establishment"""
        db = DatabaseConnection("MSSQL") \
            .with_credentials("test_user", "test_pass") \
            .connect()
        assert db.is_connected
        db.close()

    def test_invalid_credentials(self):
        """Test connection with invalid credentials"""
        with pytest.raises(DatabaseConnectionError):
            DatabaseConnection("MSSQL") \
                .with_credentials("invalid", "invalid") \
                .connect()

    def test_connection_parameters(self):
        """Test connection with custom parameters"""
        db = DatabaseConnection("POSTGRESQL") \
            .with_credentials("test_user", "test_pass") \
            .with_params(
                PORT_NUMBER=5433,
                DATABASE_NAME="test_db"
            ) \
            .connect()
        assert db.is_connected
        assert db._params["PORT_NUMBER"] == 5433
        db.close()

### 1.2 DataFrame Operation Tests
    def test_dataframe_transformations(self, sample_dataframe):
        """Test DataFrame transformation operations"""
        db = DatabaseConnection("MSSQL") \
            .with_credentials("test_user", "test_pass") \
            .connect()
        
        result = db.execute_sql_to_panda_dataframe(
            "SELECT * FROM test_table",
            return_dataframe=False
        ) \
        .transform_dataframe('standardize', columns=['value']) \
        .get_panda_dataframe()
        
        assert 'value' in result.columns
        assert abs(result['value'].mean()) < 1e-10
        assert abs(result['value'].std() - 1) < 1e-10

    def test_aggregation_operations(self, sample_dataframe):
        """Test DataFrame aggregation operations"""
        db = DatabaseConnection("MSSQL") \
            .with_credentials("test_user", "test_pass") \
            .connect()
        
        result = db.execute_sql_to_panda_dataframe(
            "SELECT * FROM test_table",
            return_dataframe=False
        ) \
        .aggregate(
            group_by=['category'],
            aggs={'value': ['sum', 'mean', 'count']},
            having={'value': ('>', 100)}
        ) \
        .get_panda_dataframe()
        
        assert all(result['value_sum'] > 100)
  

## 2. Integration Tests

### 2.1 Transaction Tests
  
class TestTransactions:
    def test_successful_transaction(self, db_connection):
        """Test successful transaction completion"""
        with db_connection.transaction():
            db_connection.execute(
                "INSERT INTO test_table (value) VALUES (?)",
                (42,)
            )
            
        result = db_connection.query_to_dataframe(
            "SELECT value FROM test_table WHERE value = ?",
            params=(42,)
        )
        assert len(result) == 1

    def test_transaction_rollback(self, db_connection):
        """Test transaction rollback on error"""
        try:
            with db_connection.transaction():
                db_connection.execute(
                    "INSERT INTO test_table (value) VALUES (?)",
                    (42,)
                )
                raise ValueError("Test error")
        except ValueError:
            pass
            
        result = db_connection.query_to_dataframe(
            "SELECT value FROM test_table WHERE value = ?",
            params=(42,)
        )
        assert len(result) == 0
  

### 2.2 Bulk Operation Tests
  
class TestBulkOperations:
    def test_bulk_insert(self, db_connection, large_dataframe):
        """Test bulk insert operation"""
        rows_before = len(db_connection.query_to_dataframe(
            "SELECT * FROM test_table"
        ))
        
        db_connection.bulk_insert(
            "test_table",
            large_dataframe,
            batch_size=1000
        )
        
        rows_after = len(db_connection.query_to_dataframe(
            "SELECT * FROM test_table"
        ))
        assert rows_after - rows_before == len(large_dataframe)

    def test_bulk_update(self, db_connection, large_dataframe):
        """Test bulk update operation"""
        db_connection.execute_batch(
            "UPDATE test_table SET value = ? WHERE id = ?",
            [(row['value'], row['id']) for _, row in large_dataframe.iterrows()]
        )
  

## 3. Performance Tests

### 3.1 Load Testing
  
class TestPerformance:
    @pytest.mark.slow
    def test_large_dataset_handling(self, db_connection):
        """Test handling of large datasets"""
        import time
        
        # Generate large dataset
        large_df = pd.DataFrame({
            'id': range(100000),
            'value': np.random.rand(100000)
        })
        
        start_time = time.time()
        db_connection.bulk_insert("test_table", large_df)
        insert_time = time.time() - start_time
        
        assert insert_time < 60  # Should complete within 60 seconds

    @pytest.mark.slow
    def test_concurrent_connections(self):
        """Test concurrent database connections"""
        import concurrent.futures
        
        def connect_and_query():
            db = DatabaseConnection("MSSQL") \
                .with_credentials("test_user", "test_pass") \
                .connect()
            result = db.query_to_dataframe("SELECT * FROM test_table LIMIT 100")
            db.close()
            return len(result)
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: connect_and_query(), range(10)))
            
        assert all(r == 100 for r in results)
  

## 4. Test Fixtures and Utilities

### 4.1 Common Fixtures
  
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    return pd.DataFrame({
        'id': range(100),
        'value': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })

@pytest.fixture
def large_dataframe():
    """Create a large DataFrame for performance testing"""
    return pd.DataFrame({
        'id': range(10000),
        'value': np.random.randn(10000),
        'category': np.random.choice(['A', 'B', 'C'], 10000)
    })

@pytest.fixture(scope="session")
def test_database():
    """Set up test database"""
    # Database setup code
    yield
    # Database cleanup code
  

### 4.2 Mock Objects
  
# tests/mocks.py
from unittest.mock import Mock, MagicMock

class MockConnection:
    def __init__(self):
        self.cursor = MagicMock()
        self.commit = Mock()
        self.rollback = Mock()
        self.close = Mock()

    def execute(self, query, params=None):
        return self.cursor

class MockCursor:
    def __init__(self, data=None):
        self.data = data or []
        self.description = [('column1',), ('column2',)]
        self.rowcount = len(self.data)

    def fetchall(self):
        return self.data

    def execute(self, query, params=None):
        pass
  ### 6.2 Common Validation Errors

- Missing required parameters
- Invalid port numbers
- Invalid hostnames/IPs
- Invalid database names
- Invalid credentials
- Dangerous SQL patterns
- Parameter count mismatches
- Invalid DataFrame operations

## 7. Best Practices

1. Always validate connection parameters before attempting connection
2. Use parameterized queries instead of string concatenation
3. Validate credentials when authentication is required
4. Validate DataFrame operations before processing
5. Handle validation errors appropriately
6. Log validation failures for debugging
7. Use type hints for better code clarity
8. Keep validation rules updated with security best practices