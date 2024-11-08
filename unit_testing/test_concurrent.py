# Description: Tests for concurrent database operations
import pytest
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
import queue
from typing import List, Dict, Any
from pydatabaseconnection import DatabaseConnection
from pydatabaseconnection.types.exceptions import DatabaseError

@pytest.mark.concurrent
class TestConcurrentOperations:
    """Tests for concurrent database operations"""

    @pytest.fixture
    def concurrent_connections(self, db_config) -> List[DatabaseConnection]:
        """Create multiple database connections"""
        connections = []
        for _ in range(5):
            conn = DatabaseConnection("MSSQL") \
                .with_credentials(
                    db_config["MSSQL"]["username"],
                    db_config["MSSQL"]["password"]
                ) \
                .connect()
            connections.append(conn)
        yield connections
        for conn in connections:
            conn.close()

    def test_concurrent_reads(self, concurrent_connections, populated_test_table):
        """Test concurrent read operations"""
        def read_data(connection: DatabaseConnection) -> pd.DataFrame:
            return connection.execute_sql_to_panda_dataframe(
                "SELECT * FROM test_table ORDER BY RAND() LIMIT 100"
            )

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=len(concurrent_connections)) as executor:
            futures = [
                executor.submit(read_data, conn) 
                for conn in concurrent_connections
            ]
            results = [f.result() for f in futures]
        end_time = time.time()

        # Verify all reads were successful and performance
        assert all(isinstance(df, pd.DataFrame) for df in results)
        assert all(len(df) == 100 for df in results)
        assert end_time - start_time < 5  # Should complete within 5 seconds

    def test_concurrent_writes(self, concurrent_connections, test_table):
        """Test concurrent write operations with transaction isolation"""
        def write_batch(
            connection: DatabaseConnection, 
            start_id: int,
            batch_size: int = 100
        ) -> bool:
            try:
                with connection.transaction():
                    df = pd.DataFrame({
                        'id': range(start_id, start_id + batch_size),
                        'value': np.random.rand(batch_size),
                        'category': np.random.choice(['A', 'B', 'C'], batch_size)
                    })
                    connection.bulk_insert("test_table", df)
                return True
            except DatabaseError:
                return False

        # Run concurrent write operations
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=len(concurrent_connections)) as executor:
            futures = [
                executor.submit(write_batch, conn, i * 1000)
                for i, conn in enumerate(concurrent_connections)
            ]
            results = [f.result() for f in futures]
        end_time = time.time()

        # Verify results
        assert all(results)  # All writes successful
        total_records = len(concurrent_connections[0].query_to_dataframe(
            "SELECT * FROM test_table"
        ))
        assert total_records == len(concurrent_connections) * 100
        assert end_time - start_time < 10  # Should complete within 10 seconds

    def test_concurrent_mixed_operations(self, concurrent_connections, test_table):
        """Test mix of concurrent read and write operations"""
        operation_results = queue.Queue()

        def mixed_operation(
            connection: DatabaseConnection, 
            op_type: str,
            start_id: int
        ) -> None:
            try:
                if op_type == 'read':
                    result = connection.execute_sql_to_panda_dataframe(
                        "SELECT * FROM test_table ORDER BY RAND() LIMIT 50"
                    )
                    operation_results.put(('read', len(result)))
                else:  # write
                    with connection.transaction():
                        df = pd.DataFrame({
                            'id': [start_id],
                            'value': [np.random.rand()],
                            'category': ['A']
                        })
                        connection.bulk_insert("test_table", df)
                        operation_results.put(('write', 1))
            except Exception as e:
                operation_results.put(('error', str(e)))

        # Run mix of operations
        operations = []
        for i in range(100):
            op_type = 'read' if i % 2 == 0 else 'write'
            conn = np.random.choice(concurrent_connections)
            operations.append((conn, op_type, i))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(mixed_operation, conn, op_type, start_id)
                for conn, op_type, start_id in operations
            ]
            _ = [f.result() for f in futures]

        # Analyze results
        results = []
        while not operation_results.empty():
            results.append(operation_results.get())

        read_count = sum(1 for op, _ in results if op == 'read')
        write_count = sum(1 for op, _ in results if op == 'write')
        error_count = sum(1 for op, _ in results if op == 'error')

        assert error_count == 0  # No operations should fail
        assert read_count + write_count == 100  # All operations accounted for

    def test_deadlock_detection(self, concurrent_connections, test_table):
        """Test deadlock detection and resolution"""
        def update_with_potential_deadlock(
            connection: DatabaseConnection,
            id_range: tuple,
            sleep_time: float
        ) -> Dict[str, Any]:
            try:
                with connection.transaction():
                    # First update
                    connection.execute("""
                        UPDATE test_table 
                        SET value = value + 1 
                        WHERE id BETWEEN ? AND ?
                    """, params=id_range)
                    
                    # Simulate processing time
                    time.sleep(sleep_time)
                    
                    # Second update with different range
                    connection.execute("""
                        UPDATE test_table 
                        SET value = value + 1 
                        WHERE id BETWEEN ? AND ?
                    """, params=(id_range[1], id_range[1] + 10))
                    
                return {"success": True, "id_range": id_range}
            except DatabaseError as e:
                return {"success": False, "error": str(e), "id_range": id_range}

        # Setup test data
        initial_data = pd.DataFrame({
            'id': range(100),
            'value': np.random.rand(100),
            'category': 'A'
        })
        concurrent_connections[0].bulk_insert("test_table", initial_data)

        # Run concurrent updates with overlapping ranges
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    update_with_potential_deadlock,
                    conn,
                    (i * 20, (i + 1) * 20),
                    np.random.rand() * 0.1
                )
                for i, conn in enumerate(concurrent_connections[:3])
            ]
            results = [f.result() for f in futures]

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        # Some operations should succeed, some might fail due to deadlock
        assert len(successful) > 0
        assert len(successful) + len(failed) == 3

    def test_connection_pool_stress(self, db_config):
        """Stress test the connection pool"""
        from pydatabaseconnection.utils.connection_pool import ConnectionPool

        pool = ConnectionPool(
            db_config,
            min_size=2,
            max_size=10
        )

        def worker_task(task_id: int) -> Dict[str, Any]:
            start_time = time.time()
            try:
                with pool.get_connection() as conn:
                    # Simulate varying workload
                    if task_id % 3 == 0:
                        time.sleep(0.1)  # Long query
                        result = conn.execute_sql_to_panda_dataframe(
                            "SELECT COUNT(*) FROM test_table"
                        )
                    else:
                        # Short query
                        result = conn.execute_sql_to_panda_dataframe(
                            "SELECT 1"
                        )
                    
                return {
                    "task_id": task_id,
                    "success": True,
                    "duration": time.time() - start_time
                }
            except Exception as e:
                return {
                    "task_id": task_id,
                    "success": False,
                    "error": str(e),
                    "duration": time.time() - start_time
                }

        # Run stress test
        num_tasks = 100
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_tasks)]
            results = [f.result() for f in futures]

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        durations = [r["duration"] for r in results]

        assert len(failed) == 0  # No tasks should fail
        assert len(successful) == num_tasks
        assert max(durations) < 5  # No task should take more than 5 seconds
        assert pool._active_connections <= pool.max_size

    @pytest.mark.slow
    def test_long_running_concurrent_operations(
        self, 
        concurrent_connections, 
        large_dataframe
    ):
        """Test long-running concurrent operations"""
        def long_running_analysis(
            connection: DatabaseConnection,
            partition: str
        ) -> Dict[str, Any]:
            try:
                start_time = time.time()
                result = connection.execute_sql_to_panda_dataframe(f"""
                    WITH RunningStats AS (
                        SELECT 
                            category,
                            value,
                            AVG(value) OVER (
                                PARTITION BY category 
                                ORDER BY id 
                                ROWS BETWEEN 100 PRECEDING AND CURRENT ROW
                            ) as moving_avg,
                            ROW_NUMBER() OVER (
                                PARTITION BY category 
                                ORDER BY value DESC
                            ) as value_rank
                        FROM test_table
                        WHERE category = ?
                    )
                    SELECT 
                        category,
                        COUNT(*) as total_records,
                        AVG(value) as avg_value,
                        AVG(moving_avg) as avg_moving_avg,
                        SUM(CASE WHEN value_rank <= 10 THEN 1 ELSE 0 END) as top_10_count
                    FROM RunningStats
                    GROUP BY category
                """, params=(partition,))
                
                return {
                    "partition": partition,
                    "success": True,
                    "results": result,
                    "duration": time.time() - start_time
                }
            except Exception as e:
                return {
                    "partition": partition,
                    "success": False,
                    "error": str(e),
                    "duration": time.time() - start_time
                }

        # Initialize test data
        concurrent_connections[0].bulk_insert("test_table", large_dataframe)

        # Run concurrent analysis
        partitions = ['A', 'B', 'C']
        with ThreadPoolExecutor(max_workers=len(partitions)) as executor:
            futures = [
                executor.submit(long_running_analysis, conn, partition)
                for conn, partition in zip(concurrent_connections, partitions)
            ]
            results = [f.result() for f in futures]

        # Verify results
        assert all(r["success"] for r in results)
        assert all(r["duration"] < 30 for r in results)  # Each analysis under 30s
        assert all(len(r["results"]) > 0 for r in results)
