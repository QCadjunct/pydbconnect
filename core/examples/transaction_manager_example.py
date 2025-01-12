"""Test example for TransactionManager functionality."""

from core.connector import DatabaseConnector
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption, IsolationLevel


def test_transaction_manager():
    """Test basic transaction manager operations."""
    print("\n=== Starting Transaction Manager Test ===")

    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        # Connect to database
        db = (
            db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(
                DRIVER="{ODBC Driver 17 for SQL Server}",
                SERVER="127.0.0.1",
                PORT_NUMBER=13001,
                DATABASE_NAME="AdventureWorks2019",
            )
            .connect_to_database()
        )

        print("Connected to AdventureWorks2019 database")

        # Test 1: Basic Transaction Context Manager
        print("\nTest 1: Basic Transaction Context Manager")
        try:
            with db.transaction_manager.transaction_scope(IsolationLevel.READ_COMMITTED) as transaction:
                # Simple select query to verify connection
                query = "SELECT TOP 1 BusinessEntityID, FirstName, LastName FROM Person.Person"
                db.execute_query_to_prettytable(query, print_result=True)
                print("Basic transaction test successful")
        except Exception as e:
            print(f"Basic transaction test failed: {str(e)}")

        # Test 2: Savepoint Operations
        print("\nTest 2: Savepoint Operations")
        try:
            with db.transaction_manager.transaction_scope(IsolationLevel.READ_COMMITTED) as transaction:
                # First query
                query1 = "SELECT TOP 1 BusinessEntityID, FirstName, LastName FROM Person.Person"
                db.execute_query_to_prettytable(query1, print_result=True)

                # Create first savepoint
                print("Creating savepoint 'point1'")
                transaction.create_savepoint("point1")

                # Second query
                query2 = "SELECT TOP 1 ProductID, Name FROM Production.Product"
                db.execute_query_to_prettytable(query2, print_result=True)

                # Demonstrate rollback
                print("Rolling back to savepoint 'point1'")
                transaction.rollback_to_savepoint("point1")
                print("Savepoint operations test successful")
        except Exception as e:
            print(f"Savepoint operations test failed: {str(e)}")

        # Test 3: Transaction Isolation Levels
        print("\nTest 3: Transaction Isolation Levels")
        try:
            with db.transaction_manager.transaction_scope(IsolationLevel.SERIALIZABLE) as transaction:
                query = "SELECT TOP 1 BusinessEntityID, FirstName, LastName FROM Person.Person"
                db.execute_query_to_prettytable(query, print_result=True)
                print("Isolation level test successful")
        except Exception as e:
            print(f"Isolation level test failed: {str(e)}")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise
    finally:
        db.close()
        print("\n=== Transaction Manager Test Completed ===")


if __name__ == "__main__":
    test_transaction_manager()
