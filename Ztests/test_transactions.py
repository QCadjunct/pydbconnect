# We will test the transactions in this file. The transactions include successful transaction completion, transaction rollback on error, nested transaction handling, transaction isolation levels, savepoint functionality, transaction state tracking, explicit transaction control methods, and transaction error handling.
# import pytest
import pytest
from pydatabaseconnection import DatabaseConnection
from pydatabaseconnection.types.exceptions import DatabaseError, TransactionError

class TestTransactions:
    """Integration tests for database transactions"""

    def test_successful_transaction(self, db_connection, test_table):
        """Test successful transaction completion"""
        with db_connection.transaction():
            db_connection.execute(
                "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                (1, 100.0, 'A')
            )
            db_connection.execute(
                "UPDATE test_table SET value = ? WHERE id = ?",
                (200.0, 1)
            )
        
        result = db_connection.query_to_dataframe(
            "SELECT * FROM test_table WHERE id = 1"
        )
        assert len(result) == 1
        assert result.iloc[0]['value'] == 200.0

    def test_transaction_rollback(self, db_connection, test_table):
        """Test transaction rollback on error"""
        initial_count = len(db_connection.query_to_dataframe(
            "SELECT * FROM test_table"
        ))
        
        with pytest.raises(DatabaseError):
            with db_connection.transaction():
                db_connection.execute(
                    "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                    (1, 100.0, 'A')
                )
                raise DatabaseError("Simulated error")
        
        final_count = len(db_connection.query_to_dataframe(
            "SELECT * FROM test_table"
        ))
        assert final_count == initial_count

    def test_nested_transactions(self, db_connection, test_table):
        """Test nested transaction handling"""
        with db_connection.transaction():
            db_connection.execute(
                "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                (1, 100.0, 'A')
            )
            
            with db_connection.transaction():
                db_connection.execute(
                    "UPDATE test_table SET value = ? WHERE id = ?",
                    (200.0, 1)
                )
        
        result = db_connection.query_to_dataframe(
            "SELECT * FROM test_table WHERE id = 1"
        )
        assert result.iloc[0]['value'] == 200.0

    def test_transaction_isolation(self, db_connection, test_table):
        """Test transaction isolation levels"""
        def read_value():
            return db_connection.query_to_dataframe(
                "SELECT value FROM test_table WHERE id = 1"
            )
        
        # First transaction
        with db_connection.transaction():
            db_connection.execute(
                "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                (1, 100.0, 'A')
            )
            
            # Verify value is visible within transaction
            result = read_value()
            assert len(result) == 1
            assert result.iloc[0]['value'] == 100.0
            
            # Rollback
            db_connection.rollback()
        
        # Verify value is not visible after rollback
        result = read_value()
        assert len(result) == 0

    def test_savepoints(self, db_connection, test_table):
        """Test savepoint functionality"""
        with db_connection.transaction():
            db_connection.execute(
                "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
                (1, 100.0, 'A')
            )
            
            db_connection.create_savepoint("sp1")
            
            db_connection.execute(
                "UPDATE test_table SET value = ? WHERE id = ?",
                (200.0, 1)
            )
            
            db_connection.rollback_to_savepoint("sp1")
            
            # Verify rolled back to original value
            result = db_connection.query_to_dataframe(
                "SELECT value FROM test_table WHERE id = 1"
            )
            assert result.iloc[0]['value'] == 100.0

    def test_transaction_state(self, db_connection):
        """Test transaction state tracking"""
        assert not db_connection.in_transaction
        
        with db_connection.transaction():
            assert db_connection.in_transaction
            
            with db_connection.transaction():
                assert db_connection.in_transaction
            
            assert db_connection.in_transaction
        
        assert not db_connection.in_transaction

    def test_explicit_transaction_methods(self, db_connection, test_table):
        """Test explicit transaction control methods"""
        db_connection.begin_transaction()
        assert db_connection.in_transaction
        
        db_connection.execute(
            "INSERT INTO test_table (id, value, category) VALUES (?, ?, ?)",
            (1, 100.0, 'A')
        )
        
        db_connection.commit()
        assert not db_connection.in_transaction
        
        result = db_connection.query_to_dataframe(
            "SELECT * FROM test_table WHERE id = 1"
        )
        assert len(result) == 1

