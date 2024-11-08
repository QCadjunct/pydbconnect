import pytest
import pandas as pd
import numpy as np
from typing import Generator, Dict, Any
from pydatabaseconnection import DatabaseConnection
from contextlib import contextmanager

@pytest.fixture(scope="session")
def db_config() -> Dict[str, Any]:
    """Database configuration for testing"""
    return {
        "MSSQL": {
            "host": "localhost",
            "port": 1433,
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass"
        },
        "POSTGRESQL": {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass"
        }
    }

@pytest.fixture(scope="function")
def db_connection(db_config) -> Generator[DatabaseConnection, None, None]:
    """Provides a database connection for testing"""
    conn = DatabaseConnection("MSSQL") \
        .with_credentials(
            db_config["MSSQL"]["username"],
            db_config["MSSQL"]["password"]
        )
    try:
        conn.connect()
        yield conn
    finally:
        if conn.is_connected:
            conn.close()

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Creates a sample DataFrame for testing"""
    return pd.DataFrame({
        'id': range(100),
        'value': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })

@pytest.fixture
def large_dataframe() -> pd.DataFrame:
    """Creates a large DataFrame for performance testing"""
    return pd.DataFrame({
        'id': range(10000),
        'value': np.random.randn(10000),
        'category': np.random.choice(['A', 'B', 'C'], 10000)
    })

@contextmanager
def create_test_table(db_connection: DatabaseConnection):
    """Creates and drops a test table"""
    db_connection.execute("""
        CREATE TABLE test_table (
            id INT PRIMARY KEY,
            value FLOAT,
            category VARCHAR(1)
        )
    """)
    try:
        yield
    finally:
        db_connection.execute("DROP TABLE IF EXISTS test_table")

@pytest.fixture
def test_table(db_connection):
    """Fixture that creates and drops a test table"""
    with create_test_table(db_connection):
        yield

@pytest.fixture
def populated_test_table(db_connection, sample_dataframe, test_table):
    """Creates a test table and populates it with sample data"""
    db_connection.bulk_insert("test_table", sample_dataframe)
    return sample_dataframe
