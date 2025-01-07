# examples/transactions/isolation_levels.py
"""Transaction isolation level examples."""

from core.connector import DatabaseConnector, DatabaseError
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption


def demonstrate_isolation_levels():
    """Show isolation level usage."""
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        with db.set_credentials_based_on_connect_option().finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="localhost",
            DATABASE_NAME="TestDB",
        ).connect_to_database():

            # Using isolation level with transaction
            with db.transaction_scope(isolation_level="SERIALIZABLE"):
                result = db.execute_query_to_dataframe("SELECT * FROM products WHERE stock > 0").to_dataframe()

                if not result.empty:
                    db.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (result.iloc[0]["id"],))

    except DatabaseError as e:
        print(f"Transaction failed: {e}")
    finally:
        db.close()
