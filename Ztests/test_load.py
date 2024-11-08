# Description: Test cases for database load handling
import pytest
import pandas as pd
import numpy as np
import time
import psutil
import os
from pydatabaseconnection import DatabaseConnection
from pydatabaseconnection.types.exceptions import DatabaseError

@pytest.mark.performance
class TestLoadPerformance:
    """Performance tests for database load handling"""

    @pytest.fixture(scope="class")
    def large_dataset(self) -> pd.DataFrame:
        """Create a large dataset for load testing"""
        return pd.DataFrame({
            'id': range(100000),
            'value': np.random.randn(100000),
            'category': np.random.choice(['A', 'B', 'C'], 100000),
            'text_data': ['Data_' + str(i) for i in range(100000)],
            'timestamp': pd.date_range('2024-01-01', periods=100000)
        })

    def test_bulk_insert_performance(self, db_connection, large_dataset):
        """Test performance of bulk insert operations"""
        batch_sizes = [100, 1000, 5000, 10000]
        results = []

        for batch_size in batch_sizes:
            # Clean up before each test
            db_connection.execute("DELETE FROM test_table")
            
            start_time = time.time()
            db_connection.bulk_insert(
                "test_table", 
                large_dataset, 
                batch_size=batch_size
            )
            end_time = time.time()
            
            results.append({
                'batch_size': batch_size,
                'duration': end_time - start_time,
                'rows_per_second': len(large_dataset) / (end_time - start_time)
            })

        # Assert reasonable performance
        best_performance = max(result['rows_per_second'] for result in results)
        assert best_performance > 1000  # At least 1000 rows per second

    def test_memory_usage(self, db_connection, large_dataset):
        """Test memory usage during large operations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform large operation
        db_connection.bulk_insert("test_table", large_dataset)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assert reasonable memory usage
        assert memory_increase < 1000  # Less than 1GB increase
        
        # Test memory cleanup
        del large_dataset
        import gc
        gc.collect()
        
        cleanup_memory = process.memory_info().rss / 1024 / 1024
        assert cleanup_memory < final_memory

    def test_query_performance(self, db_connection, large_dataset):
        """Test query performance with large datasets"""
        # Setup test data
        db_connection.bulk_insert("test_table", large_dataset)
        
        queries = {
            'simple_select': "SELECT * FROM test_table LIMIT 1000",
            'aggregation': """
                SELECT category, 
                       COUNT(*) as count, 
                       AVG(value) as avg_value
                FROM test_table 
                GROUP BY category
            """,
            'complex_join': """
                SELECT t1.category, 
                       t2.avg_value
                FROM test_table t1
                JOIN (
                    SELECT category, AVG(value) as avg_value
                    FROM test_table
                    GROUP BY category
                ) t2 ON t1.category = t2.category
                LIMIT 1000
            """
        }

        results = {}
        for query_name, query in queries.items():
            start_time = time.time()
            df = db_connection.execute_sql_to_panda_dataframe(query)
            duration = time.time() - start_time
            
            results[query_name] = {
                'duration': duration,
                'rows': len(df)
            }
            
            # Assert reasonable query performance
            assert duration < 5  # Each query should complete within 5 seconds

    def test_concurrent_load(self, db_connection, large_dataset):
        """Test database performance under concurrent load"""
        from concurrent.futures import ThreadPoolExecutor
        import random

        def random_query():
            query_type = random.choice(['select', 'aggregate', 'insert'])
            if query_type == 'select':
                return db_connection.execute_sql_to_panda_dataframe(
                    "SELECT * FROM test_table ORDER BY RAND() LIMIT 100"
                )
            elif query_type == 'aggregate':
                return db_connection.execute_sql_to_panda_dataframe(
                    "SELECT category, AVG(value) FROM test_table GROUP BY category"
                )
            else:
                db_connection.execute(
                    "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                    (random.randint(100001, 200000), random.random(), 'A')
                )

        # Setup initial data
        db_connection.bulk_insert("test_table", large_dataset)

        # Run concurrent queries
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(random_query) for _ in range(100)]
            completed = [f.result() for f in futures]
        duration = time.time() - start_time

        # Assert reasonable concurrent performance
        assert duration / 100 < 0.1  # Average 100ms per operation

    def test_data_streaming(self, db_connection, large_dataset):
        """Test performance of streaming large datasets"""
        chunk_size = 1000
        total_rows = 0
        streaming_start = time.time()

        for chunk_start in range(0, len(large_dataset), chunk_size):
            query = f"""
                SELECT *
                FROM test_table
                ORDER BY id
                OFFSET {chunk_start} ROWS
                FETCH NEXT {chunk_size} ROWS ONLY
            """
            chunk = db_connection.execute_sql_to_panda_dataframe(query)
            total_rows += len(chunk)

        streaming_duration = time.time() - streaming_start

        # Compare with bulk fetch
        bulk_start = time.time()
        bulk_result = db_connection.execute_sql_to_panda_dataframe(
            "SELECT * FROM test_table ORDER BY id"
        )
        bulk_duration = time.time() - bulk_start

        # Assert streaming completed successfully
        assert total_rows == len(bulk_result)
        
        # Log performance metrics
        print(f"\nStreaming duration: {streaming_duration:.2f}s")
        print(f"Bulk duration: {bulk_duration:.2f}s")
        print(f"Streaming overhead: {(streaming_duration/bulk_duration):.2f}x")

    @pytest.mark.slow
    def test_long_running_operations(self, db_connection, large_dataset):
        """Test performance of long-running operations"""
        # Test long-running analytical query
        start_time = time.time()
        result = db_connection.execute_sql_to_panda_dataframe("""
            WITH RankedData AS (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY category 
                                        ORDER BY value) as rank,
                       AVG(value) OVER (PARTITION BY category 
                                      ORDER BY id 
                                      ROWS BETWEEN 100 PRECEDING 
                                      AND CURRENT ROW) as moving_avg
                FROM test_table
            )
            SELECT category,
                   COUNT(*) as total_count,
                   AVG(value) as avg_value,
                   AVG(moving_avg) as avg_moving_avg,
                   SUM(CASE WHEN rank <= 10 THEN 1 ELSE 0 END) as top_10_count
            FROM RankedData
            GROUP BY category
            ORDER BY avg_value DESC
        """)
        duration = time.time() - start_time

        # Assert reasonable performance for complex analysis
        assert duration < 30  # Should complete within 30 seconds