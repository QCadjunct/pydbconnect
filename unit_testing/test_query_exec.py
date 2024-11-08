# Description: Integration tests for query execution
import pytest
import pandas as pd
from pydatabaseconnection import DatabaseConnection
from pydatabaseconnection.types.exceptions import DatabaseError

class TestQueryExecution:
    """Integration tests for query execution"""

    def test_basic_select(self, db_connection, populated_test_table):
        """Test basic SELECT query"""
        result = db_connection.execute_sql_to_panda_dataframe(
            "SELECT * FROM test_table WHERE value > ?",
            params=(0,)
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_parameterized_queries(self, db_connection, test_table):
        """Test parameterized query execution"""
        # Insert test data
        db_connection.execute(
            "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
            params=(1, 100.0, 'A')
        )
        
        # Query with different parameter types
        result = db_connection.execute_sql_to_panda_dataframe("""
            SELECT * FROM test_table 
            WHERE id = ? AND value > ? AND category = ?
        """, params=(1, 50.0, 'A'))
        
        assert len(result) == 1
        assert result.iloc[0]['value'] == 100.0

    def test_multiple_result_sets(self, db_connection, test_table):
        """Test handling multiple result sets"""
        results = db_connection.execute("""
            SELECT COUNT(*) as count FROM test_table;
            SELECT DISTINCT category FROM test_table;
        """)
        
        # First result set
        count = results.fetchone()[0]
        
        # Move to next result set
        results.nextset()
        
        # Second result set
        categories = [row[0] for row in results.fetchall()]
        
        assert isinstance(count, int)
        assert isinstance(categories, list)

    def test_query_error_handling(self, db_connection):
        """Test error handling for invalid queries"""
        # Invalid syntax
        with pytest.raises(DatabaseError) as exc_info:
            db_connection.execute("INVALID SQL")
        assert "syntax" in str(exc_info.value).lower()
        
        # Invalid table
        with pytest.raises(DatabaseError) as exc_info:
            db_connection.execute("SELECT * FROM nonexistent_table")
        assert "table" in str(exc_info.value).lower()
        
        # Invalid column
        with pytest.raises(DatabaseError) as exc_info:
            db_connection.execute("SELECT nonexistent_column FROM test_table")
        assert "column" in str(exc_info.value).lower()

    def test_large_query_results(self, db_connection, large_dataframe):
        """Test handling large query results"""
        # Insert large dataset
        db_connection.bulk_insert("test_table", large_dataframe)
        
        # Query with chunking
        chunk_size = 1000
        chunks = []
        
        for offset in range(0, len(large_dataframe), chunk_size):
            chunk = db_connection.execute_sql_to_panda_dataframe(f"""
                SELECT * FROM test_table
                ORDER BY id
                OFFSET {offset} ROWS
                FETCH NEXT {chunk_size} ROWS ONLY
            """)
            chunks.append(chunk)
        
        complete_result = pd.concat(chunks, ignore_index=True)
        assert len(complete_result) == len(large_dataframe)

    def test_query_timeout(self, db_connection, test_table):
        """Test query timeout handling"""
        with pytest.raises(DatabaseError) as exc_info:
            db_connection.execute_with_timeout("""
                WAITFOR DELAY '00:00:05';
                SELECT * FROM test_table;
            """, timeout=1)  # 1 second timeout
            
        assert "timeout" in str(exc_info.value).lower()

    def test_query_with_complex_joins(self, db_connection):
        """Test complex queries with multiple joins"""
        # Create test tables
        db_connection.execute("""
            CREATE TABLE users (
                id INT PRIMARY KEY,
                name VARCHAR(50)
            )
        """)
        
        db_connection.execute("""
            CREATE TABLE orders (
                id INT PRIMARY KEY,
                user_id INT,
                amount DECIMAL(10,2),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        try:
            # Insert test data
            db_connection.execute(
                "INSERT INTO users (id, name) VALUES (?, ?)",
                params=(1, "Test User")
            )
            
            db_connection.execute(
                "INSERT INTO orders (id, user_id, amount) VALUES (?, ?, ?)",
                params=(1, 1, 100.00)
            )
            
            # Execute complex query
            result = db_connection.execute_sql_to_panda_dataframe("""
                SELECT 
                    u.name,
                    COUNT(o.id) as order_count,
                    SUM(o.amount) as total_amount
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                GROUP BY u.name
                HAVING COUNT(o.id) > 0
            """)
            
            assert len(result) == 1
            assert result.iloc[0]['order_count'] == 1
            assert result.iloc[0]['total_amount'] == 100.00
            
        finally:
            # Cleanup
            db_connection.execute("DROP TABLE orders")
            db_connection.execute("DROP TABLE users")

    def test_query_with_different_return_types(self, db_connection, test_table):
        """Test queries returning different data types"""
        queries = {
            'scalar': ("SELECT COUNT(*) FROM test_table", int),
            'single_row': ("SELECT TOP 1 * FROM test_table", pd.Series),
            'multiple_rows': ("SELECT * FROM test_table", pd.DataFrame),
            'no_results': ("SELECT * FROM test_table WHERE 1=0", pd.DataFrame)
        }
        
        for query_type, (query, expected_type) in queries.items():
            result = db_connection.execute_sql_to_panda_dataframe(query)
            if query_type == 'scalar':
                assert isinstance(result.iloc[0, 0], expected_type)
            else:
                assert isinstance(result, expected_type)

    def test_query_with_special_characters(self, db_connection, test_table):
        """Test handling of special characters in queries"""
        special_values = [
            "Test's string",  # Single quote
            'Test"s string',  # Double quote
            "Test\string",    # Backslash
            "Test;string",    # Semicolon
            "Test--string",   # Comment markers
            "Test\n\rstring", # Newlines
            "Test\tstring",   # Tabs
        ]
        
        for value in special_values:
            db_connection.execute(
                "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                params=(len(value), 0, value)
            )
            
            result = db_connection.execute_sql_to_panda_dataframe(
                "SELECT category FROM test_table WHERE id = ?",
                params=(len(value),)
            )
            
            assert result.iloc[0]['category'] == value