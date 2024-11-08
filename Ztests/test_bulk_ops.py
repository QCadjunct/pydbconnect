# Description: Integration tests for bulk database operations
import pytest
import pandas as pd
import numpy as np
from pydatabaseconnection import DatabaseConnection
from pydatabaseconnection.types.exceptions import DatabaseError

class TestBulkOperations:
    """Integration tests for bulk database operations"""

    def test_basic_bulk_insert(self, db_connection, test_table, sample_dataframe):
        """Test basic bulk insert operation"""
        result = db_connection.bulk_insert(
            "test_table",
            sample_dataframe,
            batch_size=1000
        )
        
        inserted_data = db_connection.query_to_dataframe(
            "SELECT * FROM test_table ORDER BY id"
        )
        
        assert len(inserted_data) == len(sample_dataframe)
        pd.testing.assert_frame_equal(
            inserted_data.reset_index(drop=True),
            sample_dataframe.reset_index(drop=True),
            check_dtype=False
        )

    def test_bulk_insert_with_transaction(self, db_connection, test_table, large_dataframe):
        """Test bulk insert within transaction"""
        with db_connection.transaction():
            db_connection.bulk_insert(
                "test_table",
                large_dataframe,
                batch_size=1000
            )
            
            # Verify partial data within transaction
            partial_count = len(db_connection.query_to_dataframe(
                "SELECT * FROM test_table"
            ))
            assert partial_count == len(large_dataframe)

    def test_bulk_insert_rollback(self, db_connection, test_table, large_dataframe):
        """Test bulk insert rollback on error"""
        # Create invalid data in the middle of the DataFrame
        large_dataframe.loc[5000, 'value'] = 'invalid_value'
        
        with pytest.raises(DatabaseError):
            with db_connection.transaction():
                db_connection.bulk_insert(
                    "test_table",
                    large_dataframe,
                    batch_size=1000
                )
        
        # Verify no data was inserted
        count = len(db_connection.query_to_dataframe(
            "SELECT * FROM test_table"
        ))
        assert count == 0

    def test_bulk_insert_batch_size(self, db_connection, test_table, large_dataframe):
        """Test different batch sizes for bulk insert"""
        batch_sizes = [100, 500, 1000]
        
        for batch_size in batch_sizes:
            db_connection.execute("DELETE FROM test_table")
            
            db_connection.bulk_insert(
                "test_table",
                large_dataframe,
                batch_size=batch_size
            )
            
            inserted_count = len(db_connection.query_to_dataframe(
                "SELECT * FROM test_table"
            ))
            assert inserted_count == len(large_dataframe)

    def test_bulk_update(self, db_connection, test_table, sample_dataframe):
        """Test bulk update operation"""
        # First insert data
        db_connection.bulk_insert("test_table", sample_dataframe)
        
        # Prepare update data
        update_data = sample_dataframe.copy()
        update_data['value'] = update_data['value'] * 2
        
        # Perform bulk update
        with db_connection.transaction():
            for _, row in update_data.iterrows():
                db_connection.execute(
                    "UPDATE test_table SET value = ? WHERE id = ?",
                    (row['value'], row['id'])
                )
        
        # Verify updates
        updated_data = db_connection.query_to_dataframe(
            "SELECT * FROM test_table ORDER BY id"
        )
        pd.testing.assert_frame_equal(
            updated_data.reset_index(drop=True),
            update_data.reset_index(drop=True),
            check_dtype=False
        )

    def test_bulk_delete(self, db_connection, test_table, sample_dataframe):
        """Test bulk delete operation"""
        # First insert data
        db_connection.bulk_insert("test_table", sample_dataframe)
        
        # Delete in batches
        with db_connection.transaction():
            db_connection.execute_batch(
                "DELETE FROM test_table WHERE id = ?",
                [(id,) for id in sample_dataframe['id'][::2]]  # Delete every other record
            )
        
        # Verify remaining records
        remaining_data = db_connection.query_to_dataframe(
            "SELECT * FROM test_table ORDER BY id"
        )
        assert len(remaining_data) == len(sample_dataframe) // 2

    def test_bulk_operation_with_different_types(self, db_connection, test_table):
        """Test bulk operations with different data types"""
        test_data = pd.DataFrame({
            'id': range(100),
            'int_val': np.random.randint(1, 100, 100),
            'float_val': np.random.rand(100),
            'str_val': [f'str_{i}' for i in range(100)],
            'date_val': pd.date_range('2024-01-01', periods=100),
            'bool_val': np.random.choice([True, False], 100)
        })
        
        # Create table with multiple types
        db_connection.execute("""
            CREATE TABLE type_test (
                id INT PRIMARY KEY,
                int_val INT,
                float_val FLOAT,
                str_val VARCHAR(50),
                date_val DATE,
                bool_val BIT
            )
        """)
        
        try:
            # Perform bulk insert
            db_connection.bulk_insert("type_test", test_data)
            
            # Verify data
            result = db_connection.query_to_dataframe(
                "SELECT * FROM type_test ORDER BY id"
            )
            
            assert len(result) == len(test_data)
            assert all(result['int_val'].dtype == np.int64)
            assert all(result['float_val'].dtype == np.float64)
            
        finally:
            db_connection.execute("DROP TABLE type_test")

    def test_bulk_insert_error_handling(self, db_connection, test_table):
        """Test error handling during bulk insert"""
        # Create invalid data
        invalid_data = pd.DataFrame({
            'id': range(100),
            'value': ['invalid' if i == 50 else i for i in range(100)],
            'category': ['A'] * 100
        })
        
        with pytest.raises(DatabaseError) as exc_info:
            db_connection.bulk_insert("test_table", invalid_data)
        
        assert "invalid" in str(exc_info.value).lower()