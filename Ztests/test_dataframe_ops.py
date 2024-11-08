# We will test the dataframe operations in this file. The dataframe operations include basic query to dataframe conversion, standardization transformation, null value filling transformation, custom transformation function, dataframe aggregation operations, dataframe export to different formats, transformation history and undo, dataframe description functionality, error handling in dataframe operations, and multiple chained dataframe operations.
import pytest
import pandas as pd
import numpy as np
from ..core import DatabaseConnection
from ..types.exceptions import DataFrameOperationError

class TestDataFrameOperations:
    """Unit tests for DataFrame operations"""

    def test_basic_query_to_dataframe(self, db_connection, populated_test_table):
        """Test basic SQL query to DataFrame conversion"""
        df = db_connection.execute_sql_to_panda_dataframe(
            "SELECT * FROM test_table",
            return_dataframe=True
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert all(col in df.columns for col in ['id', 'value', 'category'])

    def test_transform_standardize(self, db_connection, sample_dataframe):
        """Test standardization transformation"""
        result = db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .transform_dataframe('standardize', columns=['value']) \
            .get_panda_dataframe()
        
        assert abs(result['value'].mean()) < 1e-10
        assert abs(result['value'].std() - 1) < 1e-10

    def test_transform_fillna(self, db_connection):
        """Test null value filling transformation"""
        df = pd.DataFrame({
            'id': range(5),
            'value': [1.0, None, 3.0, None, 5.0]
        })
        
        result = db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .transform_dataframe('fillna', value=0) \
            .get_panda_dataframe()
        
        assert not result['value'].isnull().any()

    def test_transform_custom(self, db_connection, sample_dataframe):
        """Test custom transformation function"""
        def custom_transform(df):
            return df.assign(doubled_value=df['value'] * 2)
        
        result = db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .transform_dataframe(custom_transform) \
            .get_panda_dataframe()
        
        assert 'doubled_value' in result.columns
        assert all(result['doubled_value'] == result['value'] * 2)

    def test_aggregation(self, db_connection, populated_test_table):
        """Test DataFrame aggregation operations"""
        result = db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .aggregate(
                group_by=['category'],
                aggs={'value': ['sum', 'mean', 'count']},
                having={'value': ('>', 0)}
            ) \
            .get_panda_dataframe()
        
        assert 'category' in result.columns
        assert 'value_sum' in result.columns
        assert 'value_mean' in result.columns
        assert 'value_count' in result.columns

    def test_export_formats(self, db_connection, sample_dataframe, tmp_path):
        """Test DataFrame export to different formats"""
        # CSV export
        csv_path = tmp_path / "test.csv"
        db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .export_dataframe('csv', str(csv_path))
        
        assert csv_path.exists()
        
        # Excel export
        excel_path = tmp_path / "test.xlsx"
        db_connection \
            .export_dataframe('excel', str(excel_path))
        
        assert excel_path.exists()

    def test_transform_history(self, db_connection, sample_dataframe):
        """Test transformation history and undo"""
        result = db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False,
                store_history=True
            ) \
            .transform_dataframe('standardize', columns=['value']) \
            .transform_dataframe(lambda df: df.assign(new_col=1)) \
            .undo_transformation() \
            .get_panda_dataframe()
        
        assert 'new_col' not in result.columns
        assert abs(result['value'].std() - 1) < 1e-10

    def test_describe_dataframe(self, db_connection, sample_dataframe, capsys):
        """Test DataFrame description functionality"""
        db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .describe_dataframe()
        
        captured = capsys.readouterr()
        assert "DataFrame Description" in captured.out
        assert "DataFrame Info" in captured.out

    def test_error_handling(self, db_connection):
        """Test error handling in DataFrame operations"""
        with pytest.raises(DataFrameOperationError):
            db_connection \
                .transform_dataframe('standardize')  # No DataFrame available

        with pytest.raises(DataFrameOperationError):
            db_connection \
                .execute_sql_to_panda_dataframe(
                    "SELECT * FROM test_table",
                    return_dataframe=False
                ) \
                .transform_dataframe('invalid_transform')

    def test_chained_operations(self, db_connection, sample_dataframe):
        """Test multiple chained DataFrame operations"""
        result = db_connection \
            .execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table",
                return_dataframe=False
            ) \
            .transform_dataframe('fillna', value=0) \
            .transform_dataframe('standardize', columns=['value']) \
            .aggregate(
                group_by=['category'],
                aggs={'value': ['mean', 'std']}
            ) \
            .transform_dataframe(lambda df: df.round(4)) \
            .get_panda_dataframe()
        
        assert not result.isnull().any().any()
        assert all(col in result.columns for col in ['value_mean', 'value_std'])