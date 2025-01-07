# examples/transactions/savepoints.py
"""Transaction savepoint examples."""

from core.connector import DatabaseConnector, DatabaseError
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption, FileFormat, IsolationLevel


def demonstrate_savepoints():
    """Show savepoint usage."""
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        with db.set_credentials_based_on_connect_option().finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=15001,
            DATABASE_NAME="TestTransactionsDB",
        ).connect_to_database():

            # Complex transaction with savepoints
            with db.transaction_scope(isolation_level=IsolationLevel.SERIALIZABLE):
                # Create order
                db.execute("INSERT INTO orders (CustomerId, total) VALUES (?, ?)", (1, 500.00))
                db.create_savepoint("order_created")

                try:
                    # Update inventory
                    db.execute("UPDATE inventory SET stock = stock - 1 WHERE product_id = ?", (101,))
                    db.create_savepoint("inventory_updated")

                    # Process payment
                    db.execute("UPDATE accounts SET balance = balance - ? WHERE CustomerId = ?", (500.00, 1))
                except DatabaseError:
                    # Rollback to after order creation
                    db.rollback("order_created")
                    raise

    except DatabaseError as e:
        print(f"Transaction failed: {e}")
    finally:
        db.close()
