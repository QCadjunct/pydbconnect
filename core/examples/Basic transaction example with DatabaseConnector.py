# examples/transactions/basic_transaction.py
"""Basic transaction example with DatabaseConnector."""

from core.connector import DatabaseConnector, DatabaseError
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption


def demonstrate_basic_transaction():
    """Show basic transaction usage."""
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        with db.set_credentials_based_on_connect_option().finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="localhost",
            PORT_NUMBER=13001,
            DATABASE_NAME="AdventureWorks2019",
        ).connect_to_database():

            # Using transaction scope
            with db.transaction_scope():
                db.execute("INSERT INTO customers (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
                db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100.00, 1))

    except DatabaseError as e:
        print(f"Transaction failed: {e}")
    finally:
        db.close()
