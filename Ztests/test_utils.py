# Description: Tests for utility functions and decorators in the package
import pytest
import pandas as pd
import numpy as np
from typing import Dict, Any
from pathlib import Path
from ..utils.decorators import preload_default_parameters
from ..utils.validation import (
    validate_connection_params,
    validate_credentials,
    validate_port
)
from ..utils.helpers import (
    load_json_config,
    parse_connection_string,
    mask_credentials
)
from ..types.exceptions import ValidationError, DatabaseError

class TestValidationUtils:
    """Tests for validation utility functions"""

    def test_connection_params_validation(self):
        """Test validation of connection parameters"""
        # Valid parameters
        valid_params = {
            "SERVER": "localhost",
            "PORT_NUMBER": 1433,
            "DATABASE_NAME": "test_db",
            "DRIVER": "{ODBC Driver}"
        }
        required_params = {"SERVER", "PORT_NUMBER", "DATABASE_NAME"}
        
        # Should not raise exception
        validate_connection_params(valid_params, required_params)

        # Missing required parameter
        invalid_params = valid_params.copy()
        del invalid_params["SERVER"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_connection_params(invalid_params, required_params)
        assert "Missing required parameters" in str(exc_info.value)

    def test_credential_validation(self):
        """Test validation of credentials"""
        # Valid credentials
        assert validate_credentials("user", "pass", True)

        # Invalid cases
        invalid_cases = [
            (None, "pass", True),
            ("user", None, True),
            ("", "pass", True),
            ("user", "", True),
            (None, None, True)
        ]

        for username, password, required in invalid_cases:
            assert not validate_credentials(username, password, required)

        # Non-required credentials
        assert validate_credentials(None, None, False)

    def test_port_validation(self):
        """Test port number validation"""
        # Valid ports
        valid_ports = [1, 1433, 3306, 5432, 65535]
        for port in valid_ports:
            assert validate_port(port)

        # Invalid ports
        invalid_ports = [0, -1, 65536, 99999]
        for port in invalid_ports:
            assert not validate_port(port)

        # None port (optional)
        assert validate_port(None)

class TestDecorators:
    """Tests for decorator functions"""

    def test_preload_default_parameters_decorator(self):
        """Test preload_default_parameters decorator"""
        class TestClass:
            def __init__(self):
                self._default_params = {
                    "param1": "default1",
                    "param2": "default2"
                }

            def _get_default_parameters(self) -> Dict[str, Any]:
                return self._default_params

            @preload_default_parameters(_get_default_parameters)
            def test_method(self, **params):
                return params

        test_obj = TestClass()

        # Test with defaults only
        result = test_obj.test_method()
        assert result == test_obj._default_params

        # Test with custom parameters
        custom_params = {"param1": "custom1", "param3": "custom3"}
        result = test_obj.test_method(**custom_params)
        expected = test_obj._default_params.copy()
        expected.update(custom_params)
        assert result == expected

        # Test with use_default_parameters=False
        result = test_obj.test_method(use_default_parameters=False, **custom_params)
        assert result == custom_params

class TestHelperFunctions:
    """Tests for helper utility functions"""

    def test_load_json_config(self, tmp_path):
        """Test JSON configuration loading"""
        # Create test config file
        config_data = {
            "database": {
                "host": "localhost",
                "port": 1433
            },
            "credentials": {
                "username": "test_user"
            }
        }
        
        config_file = tmp_path / "test_config.json"
        config_file.write_text("""{
            "database": {
                "host": "localhost",
                "port": 1433
            },
            "credentials": {
                "username": "test_user"
            }
        }""")

        # Test loading
        loaded_config = load_json_config(config_file)
        assert loaded_config == config_data

        # Test with non-existent file
        with pytest.raises(ValueError):
            load_json_config(tmp_path / "nonexistent.json")

        # Test with invalid JSON
        invalid_config = tmp_path / "invalid_config.json"
        invalid_config.write_text("invalid json content")
        
        with pytest.raises(ValueError):
            load_json_config(invalid_config)

    def test_parse_connection_string(self):
        """Test connection string parsing"""
        # Test ODBC style connection string
        odbc_string = "DRIVER={SQL Server};SERVER=localhost;DATABASE=test_db;UID=user;PWD=pass"
        parsed = parse_connection_string(odbc_string)
        
        assert parsed["DRIVER"] == "{SQL Server}"
        assert parsed["SERVER"] == "localhost"
        assert parsed["DATABASE"] == "test_db"
        assert parsed["UID"] == "user"
        assert parsed["PWD"] == "pass"

        # Test PostgreSQL style connection string
        pg_string = "host=localhost port=5432 dbname=test_db user=postgres password=pass"
        parsed = parse_connection_string(pg_string)
        
        assert parsed["host"] == "localhost"
        assert parsed["port"] == "5432"
        assert parsed["dbname"] == "test_db"
        assert parsed["user"] == "postgres"
        assert parsed["password"] == "pass"

    def test_mask_credentials(self):
        """Test credential masking in connection strings"""
        # Test ODBC style
        odbc_string = "DRIVER={SQL Server};SERVER=localhost;DATABASE=test_db;UID=user;PWD=sensitive_password"
        masked = mask_credentials(odbc_string)
        
        assert "sensitive_password" not in masked
        assert "PWD=****" in masked
        assert "UID=user" in masked

        # Test PostgreSQL style
        pg_string = "host=localhost port=5432 dbname=test_db user=postgres password=sensitive_password"
        masked = mask_credentials(pg_string)
        
        assert "sensitive_password" not in masked
        assert "password=****" in masked
        assert "user=postgres" in masked

class TestDataFrameUtils:
    """Tests for DataFrame utility functions"""

    def test_dataframe_to_sql_types(self):
        """Test DataFrame to SQL type mapping"""
        from pydatabaseconnection.utils.dataframe_utils import map_dtype_to_sql

        test_df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'str_col': ['a', 'b', 'c'],
            'date_col': pd.date_range('2024-01-01', periods=3),
            'bool_col': [True, False, True]
        })

        type_mapping = {
            'int_col': 'INT',
            'float_col': 'FLOAT',
            'str_col': 'VARCHAR(MAX)',
            'date_col': 'DATETIME',
            'bool_col': 'BIT'
        }

        for col in test_df.columns:
            sql_type = map_dtype_to_sql(test_df[col].dtype)
            assert sql_type == type_mapping[col]

    def test_chunked_dataframe_iterator(self):
        """Test DataFrame chunking utility"""
        from pydatabaseconnection.utils.dataframe_utils import chunk_dataframe

        # Create test DataFrame
        df = pd.DataFrame({
            'id': range(1000),
            'value': np.random.rand(1000)
        })

        # Test different chunk sizes
        chunk_sizes = [10, 100, 500]
        for chunk_size in chunk_sizes:
            chunks = list(chunk_dataframe(df, chunk_size))
            
            # Verify chunk sizes
            assert all(len(chunk) <= chunk_size for chunk in chunks)
            assert sum(len(chunk) for chunk in chunks) == len(df)
            
            # Verify data integrity
            reconstructed = pd.concat(chunks).reset_index(drop=True)
            pd.testing.assert_frame_equal(df, reconstructed)

    def test_dataframe_validation(self):
        """Test DataFrame validation utilities"""
        from pydatabaseconnection.utils.dataframe_utils import validate_dataframe

        # Valid DataFrame
        valid_df = pd.DataFrame({
            'id': range(10),
            'name': ['User' + str(i) for i in range(10)]
        })
        validate_dataframe(valid_df)

        # DataFrame with null values
        invalid_df = pd.DataFrame({
            'id': range(10),
            'name': ['User' + str(i) if i % 2 else None for i in range(10)]
        })
        with pytest.raises(ValidationError):
            validate_dataframe(invalid_df, allow_nulls=False)

        # DataFrame with duplicate indices
        invalid_df = pd.DataFrame({
            'id': [1, 1, 2, 3],
            'name': ['A', 'B', 'C', 'D']
        })
        with pytest.raises(ValidationError):
            validate_dataframe(invalid_df, check_unique_index='id')

class TestLoggingUtils:
    """Tests for logging utilities"""

    def test_query_logging(self, caplog):
        """Test query logging functionality"""
        from pydatabaseconnection.utils.logging_utils import log_query

        # Test basic query logging
        query = "SELECT * FROM users WHERE id = ?"
        params = (1,)
        log_query(query, params)
        
        assert "Executing query" in caplog.text
        assert query in caplog.text

        # Test sensitive data masking
        sensitive_query = "SELECT * FROM users WHERE password = 'secret'"
        log_query(sensitive_query)
        
        assert "secret" not in caplog.text
        assert "'****'" in caplog.text

    def test_performance_logging(self, caplog):
        """Test performance logging functionality"""
        from pydatabaseconnection.utils.logging_utils import log_performance

        @log_performance
        def slow_function():
            import time
            time.sleep(0.1)
            return "result"

        result = slow_function()
        
        assert "Function 'slow_function' took" in caplog.text
        assert "ms to execute" in caplog.text
        assert result == "result"
